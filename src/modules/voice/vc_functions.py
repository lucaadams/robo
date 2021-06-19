import asyncio
import random
import youtube_dl
import pafy
import discord

import bot
from data import data
import verbose.embeds


FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'
}

YOUTUBE_DL_OPTIONS = {
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

DEFAULT_GUILD_VC_DATA = {
    'voice_client': None, 'guild_queue': [], 'loop': False, 'enable_np': True
}

guild_vc_data = {}


async def vc_command_handler(message):
    guild_id = str(message.guild.id)
    if guild_id not in guild_vc_data:
        guild_vc_data[guild_id] = DEFAULT_GUILD_VC_DATA.copy()

    guild_vc_data[guild_id]["guild_queue"]

    try:
        second_parameter = message.content.split(" ")[2]
    # if no second parameter specified, send error message
    except IndexError:
        await message.channel.send(embed=verbose.embeds.embed_error_message("Incomplete command."))
        return

    # get required function that corresponds to 
    if second_parameter in COMMAND_HANDLER_DICT.keys():
        await COMMAND_HANDLER_DICT[second_parameter](message)
    else:
        await message.channel.send(embed=verbose.embeds.embed_error_message("Invalid command."))


async def join_voice_channel(message):
    guild_id = str(message.guild.id)

    try:
        channel = message.author.voice.channel
    # if user not in a vc, catch error and reply on discord
    except AttributeError:
        await message.channel.send(embed=verbose.embeds.embed_sorry_message("You must be in a voice channel to use this command."))
        return

    try:
        guild_vc_data[guild_id]["voice_client"] = await channel.connect()
    # if already in a channel, catch error and reply on discord
    except discord.errors.ClientException:
        await message.channel.send(embed=verbose.embeds.embed_sorry_message("I am already in a voice channel."))
        return

    await play_from_yt(message)


async def leave_voice_channel(message):
    guild_id = str(message.guild.id)

    # checks if bot is in a vc, if not then reply on discord
    try:
        if not guild_vc_data[guild_id]["voice_client"].is_connected():
            await message.channel.send(embed=verbose.embeds.embed_sorry_message("I am not currently in any voice channel."))
        await guild_vc_data[guild_id]["voice_client"].disconnect()
    # catch error if there is no key "voice client" in guild_vc_data. This only happens when user tries to get bot to leave before having asked them to join.
    except AttributeError:
        await message.channel.send(embed=verbose.embeds.embed_sorry_message("I am not currently in any voice channel."))


async def play_from_yt(message):
    """
    use pafy to play audio from youtube straight into the discord voice client (no download required)
    """
    guild_id = str(message.guild.id)
    guild_queue = guild_vc_data[guild_id]["guild_queue"]

    # get the metadata for the oldest song in the queue (the one that is going to be played)
    try:
        song_request_metadata = guild_queue[0]
    except IndexError:
        await message.channel.send(embed=verbose.embeds.embed_response("The queue is empty.", "I will stay in the voice channel... in silence..."))
        return

    voice_client = guild_vc_data[guild_id]["voice_client"]

    # use pafy to pipe youtube audio into the voice client
    audio = pafy.new(
        song_request_metadata['id'], ydl_opts=YOUTUBE_DL_OPTIONS).getbestaudio()
    voice_client.play(discord.FFmpegPCMAudio(
        audio.url, options=FFMPEG_OPTIONS), after=lambda e: asyncio.run_coroutine_threadsafe(on_playback_finished(message), bot.CLIENT.loop))

    if guild_vc_data[guild_id]["enable_np"]:
        await message.channel.send(embed=embed_youtube_info(song_request_metadata))


async def on_playback_finished(message):
    """
    when current song stops playing, get the next song ready
    """
    guild_id = str(message.guild.id)

    if not guild_vc_data[guild_id]["loop"]:
        try:
            guild_vc_data[guild_id]["guild_queue"].pop(0)
        except IndexError:
            await message.channel.send(embed=verbose.embeds.embed_response("Your queue has finished playing.", "I will stay in the voice channel... in silence..."))

    await play_from_yt(message)


async def continue_to_next_req(message):
    guild_id = str(message.guild.id)

    try:
        guild_vc_data[guild_id]["voice_client"].stop()
    except AttributeError:
        await message.channel.send(embed=verbose.embeds.embed_sorry_message("I am not currently in any voice channel."))
        return

    # the "after" parameter in the voice_client.play method will take care of playing the next song


async def add_song_to_queue(message):
    guild_id = str(message.guild.id)
    user_song_request_list = message.content.split(" ")[3:]
    user_song_request = " ".join(user_song_request_list)

    if len(user_song_request) < 1:
        await message.channel.send(embed=verbose.embeds.embed_error_message("No request specified."))
        return

    # Add the video metadata to queue
    # use channel.typing so the user knows something is happening - it might take a while to download metadata depending on internet speed
    async with message.channel.typing():
        with youtube_dl.YoutubeDL() as ytdl:
            if check_if_url(user_song_request):
                user_song_request_dict = ytdl.extract_info(
                    user_song_request, download=False)
                video_to_add = user_song_request_dict
            else:
                user_song_request_dict = ytdl.extract_info(
                    f"ytsearch:{user_song_request}", download=False)
                video_to_add = user_song_request_dict['entries'][0]

        guild_vc_data[guild_id]["guild_queue"].append(video_to_add)

    await message.channel.send(embed=verbose.embeds.embed_successful_action(
        f"Added [{video_to_add['title']}]({video_to_add['webpage_url']}) to the queue"))


async def remove_from_queue(message):
    guild_id = str(message.guild.id)

    try:
        index_to_remove = int(message.content.split(" ")[3])
    except ValueError:
        await message.channel.send(embed=verbose.embeds.embed_error_message("Must specify valid queue index."))
        return

    try:
        removed_song = guild_vc_data[guild_id]["guild_queue"].pop(index_to_remove - 1)
        await message.channel.send(
            embed=verbose.embeds.embed_successful_action(f"[{removed_song['title']}] \
                ({removed_song['webpage_url']}) has been removed from the queue"))
    except IndexError:
        await message.channel.send(embed=verbose.embeds.embed_error_message("That queue index does not exist."))
        return

    # if they want to remove currently playing song, then continue to next song
    if index_to_remove == 1:
        try:
            guild_vc_data[guild_id]["voice_client"].stop()
        except AttributeError:
            return

        await play_from_yt(message)


async def send_queue(message):
    """
    sends songs from a specified queue, or the current queue if no queue is specified
    """
    print("sending queue of " + str(message.guild.name))
    guild_id = str(message.guild.id)
    desc = ""
    num = 1

    # if no queue specified, send songs from the current queue
    specific_queue = " ".join(message.content.split(" ")[3:])
    if len(specific_queue) == 0:
        for metadata in guild_vc_data[guild_id]["guild_queue"]:
            desc += f"{num} - [{metadata['title']}]({metadata['webpage_url']})\n"
            num += 1
        if desc == "":
            await message.channel.send(embed=verbose.embeds.embed_response_without_title("Your queue is currently empty."))
        else:
            await message.channel.send(embed=verbose.embeds.embed_response("Up next", desc))
        return

    # if the user specified a queue, then check if it exists in the guild_data json file and get queue info from there instead
    guild_data = data.get_guild_data(guild_id)
    if specific_queue in guild_data["saved_queues"]:
        for metadata in guild_data["saved_queues"][specific_queue]:
            desc += f"{num} - [{metadata['title']}]({metadata['webpage_url']})\n"
            num += 1
        if desc == "":
            await message.channel.send(embed=verbose.embeds.embed_response_without_title("That queue is currently empty."))
        else:
            await message.channel.send(embed=verbose.embeds.embed_response(f"Queue `{specific_queue}`:", desc))
        return

    await message.channel.send(embed=verbose.embeds.embed_error_message("You do not have a saved queue with that name."))


async def send_queue_list(message):
    """
    send a list of saved queues in the user's guild
    """
    guild_id = str(message.guild.id)
    guild_data = data.get_guild_data(guild_id)

    desc = ""

    for queue_name in guild_data["saved_queues"]:
        raw_queue_duration = 0
        for song in guild_data['saved_queues'][queue_name]:
            raw_queue_duration += song["duration"]

        total_time_mins = raw_queue_duration // 60
        time_secs = raw_queue_duration % 60
        time_hours = total_time_mins // 60
        time_mins = total_time_mins % 60

        queue_duration = f"{time_hours}h {time_mins}m {time_secs}s" if time_hours != 0 else f"{time_mins}m {time_secs}s"

        desc += f"• `{queue_name}` - {len(guild_data['saved_queues'][queue_name])} songs | {queue_duration}\n"

    if desc == "":
        await message.channel.send(embed=verbose.embeds.embed_response_without_title("You don't currently have any saved queues."))
    else:
        await message.channel.send(embed=verbose.embeds.embed_response("Saved queues:", desc))


async def play_queue(message):
    """
    replace current queue with a specified custom queue from the guild_data.json file
    """
    guild_id = str(message.guild.id)
    guild_data = data.get_guild_data(guild_id)

    try:
        queue_to_play = " ".join(message.content.split(" ")[3:])
    except IndexError:
        await message.channel.send(embed=verbose.embeds.embed_error_message("You must specify a queue to play."))
        return

    if queue_to_play not in guild_data["saved_queues"]:
        await message.channel.send(embed=verbose.embeds.embed_error_message("That queue does not exist."))
        return

    guild_vc_data[guild_id]["guild_queue"] = guild_data["saved_queues"][queue_to_play].copy()

    try:
        guild_vc_data[guild_id]["voice_client"].stop()
    except AttributeError:
        await message.channel.send(embed=verbose.embeds.embed_response("Queue set.", "Type `!robo vc join` to start listening."))
        return

    await play_from_yt(message)


async def save_queue(message):
    """
    save current queue as a preset with a name of the user's choice
    """
    guild_id = str(message.guild.id)

    if len(guild_vc_data[guild_id]["guild_queue"]) < 1:
        await message.channel.send(embed=verbose.embeds.embed_sorry_message("Your current queue is empty."))
        return

    queue_name = " ".join(message.content.split(" ")[3:])
    guild_data = data.get_guild_data(guild_id)
    guild_data["saved_queues"][queue_name] = guild_vc_data[guild_id]["guild_queue"].copy()
    data.set_guild_data(guild_id, guild_data)

    await message.channel.send(embed=verbose.embeds.embed_successful_action(
        f"Saved current queue preset as `{queue_name}`"))


async def shuffle_queue(message):
    guild_id = str(message.guild.id)
    if guild_vc_data[guild_id]["voice_client"] is not None:
        guild_queue_to_shuffle = guild_vc_data[guild_id]["guild_queue"].copy()
        guild_queue_to_shuffle.pop(0)
        random.shuffle(guild_queue_to_shuffle)
        guild_vc_data[guild_id]["guild_queue"][1:] = guild_queue_to_shuffle
    else:
        random.shuffle(guild_vc_data[guild_id]["guild_queue"])

    await message.channel.send(embed=verbose.embeds.embed_response_without_title_custom_emote(f"Queue shuffled.", ":twisted_rightwards_arrows:"))


async def toggle_np(message):
    guild_id = str(message.guild.id)

    if guild_vc_data[guild_id]["enable_np"]:
        guild_vc_data[guild_id]["enable_np"] = False
        await message.channel.send(embed=verbose.embeds.embed_response_without_title_custom_emote("'Now playing' message disabled.", ":ok_hand:"))

    elif not guild_vc_data[guild_id]["enable_np"]:
        guild_vc_data[guild_id]["enable_np"] = True
        await message.channel.send(embed=verbose.embeds.embed_response_without_title_custom_emote("'Now playing' message enabled.", ":ok_hand:"))


async def toggle_loop(message):
    guild_id = str(message.guild.id)

    if guild_vc_data[guild_id]["loop"]:
        guild_vc_data[guild_id]["loop"] = False
        await message.channel.send(embed=verbose.embeds.embed_response_without_title_custom_emote("Loop disabled.", ":repeat:"))
    else:
        guild_vc_data[guild_id]["loop"] = True
        await message.channel.send(embed=verbose.embeds.embed_response_without_title_custom_emote("Loop enabled.", ":repeat:"))


def embed_youtube_info(metadata):
    youtube_info_embed = discord.Embed(
        title=f"{metadata['title']} - {metadata['uploader']}",
        colour=discord.Color(0xeb4034)
    )

    time_mins = metadata["duration"] // 60
    time_mins = f"0{time_mins}" if time_mins < 10 else time_mins

    time_secs = metadata["duration"] % 60
    time_secs = f"0{time_secs}" if time_secs < 10 else time_secs

    youtube_info_embed.set_author(
        icon_url="https://www.iconpacks.net/icons/2/free-youtube-logo-icon-2431-thumb.png", name=" Now playing:")
    youtube_info_embed.set_thumbnail(url=metadata["thumbnail"])
    youtube_info_embed.set_footer(
        text=f"⠀     👁️ {metadata['view_count']}⠀         |⠀         👍 {metadata['like_count']}⠀         |⠀         👎 {metadata['dislike_count']}⠀         |⠀         ⏱️ {time_mins}:{time_secs}⠀     ")

    return youtube_info_embed


def check_if_url(string):
    return string.startswith("http") or string.startswith("www")


COMMAND_HANDLER_DICT = {
    "join": join_voice_channel,
    "leave": leave_voice_channel,
    "add": add_song_to_queue,
    "skip": continue_to_next_req,
    "next": continue_to_next_req,
    "queue": send_queue,
    "remove": remove_from_queue,
    "save-queue": save_queue,
    "shuffle": shuffle_queue,
    "queue-list": send_queue_list,
    "play-queue": play_queue,
    "toggle-np": toggle_np,
    "loop": toggle_loop,
}
