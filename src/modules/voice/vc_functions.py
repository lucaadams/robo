import asyncio
import time
import random
import copy
import youtube_dl
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pafy
import logging
import discord

import bot
from data import data
from data import __secrets
from command_prefix import COMMAND_PREFIX
import verbose.embeds
from modules.voice.song_queue import Song, QueueMessage


FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn',
}

YOUTUBE_DL_OPTIONS = {
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

DEFAULT_GUILD_VC_DATA = {
    'voice_client': None, 'guild_queue': [], 'active_queue_message': None, 'now_playing': None, 'loop': False, 'queue_loop': False, 'enable_np': True, 'vote_skips': 0,
}

guild_vc_data = {}

spotipy_client_id = __secrets["spotipy_client_id"]
spotipy_client_secret = __secrets["spotipy_client_secret"]
if spotipy_client_id == "REPLACE THIS TEXT WITH YOUR SPOTIPY CLEINT ID" or \
    spotipy_client_secret == "REPLACE THIS TEXT WITH YOUR SPOTIPY CLEINT SECRET":
    logging.info(
        "Your spotipy client id and/or secret have not been set. Adding songs or playlists from spotify will not work. \
            To get a client id and/or secret, go to https://developer.spotify.com/dashboard/login and make an app.")

sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=spotipy_client_id, client_secret=spotipy_client_secret))


async def vc_command_handler(message):
    guild_id = str(message.guild.id)
    if guild_id not in guild_vc_data:
        guild_vc_data[guild_id] = copy.deepcopy(DEFAULT_GUILD_VC_DATA)

    try:
        second_parameter = message.content.split(" ")[2]
    # if no second parameter specified, send error message
    except IndexError:
        await message.channel.send(embed=verbose.embeds.embed_warning_message("Incomplete command."))
        return

    # get required function that corresponds to 
    if second_parameter in COMMAND_HANDLER_DICT.keys():
        await COMMAND_HANDLER_DICT[second_parameter](message)
    else:
        await message.channel.send(embed=verbose.embeds.embed_warning_message("Invalid command."))


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
        song_request: Song = guild_queue[0]
    except IndexError:
        await message.channel.send(embed=verbose.embeds.embed_response("The queue is empty.", "I will stay in the voice channel... in silence..."))
        return

    if not song_request.youtube_metadata: # if i dont have the metadata
        with youtube_dl.YoutubeDL() as ytdl:
            if check_if_url(song_request.url, "youtube"):
                song_request_metadata = ytdl.extract_info(
                    song_request.url, download=False)
                song_request.youtube_metadata = song_request_metadata

            else:
                results = ytdl.extract_info(
                    f"ytsearch:{song_request.name}", download=False)
                if len(results['entries']) == 0:
                    await message.channel.send(embed=verbose.embeds.embed_warning_message("Sorry, I could not find a song on youtube with that name."))
                song_request_metadata = results['entries'][0]
                song_request.youtube_metadata = song_request_metadata
    else:
        song_request_metadata = song_request.youtube_metadata

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
            removed_song = guild_vc_data[guild_id]["guild_queue"].pop(0)
        except IndexError:
            await message.channel.send(embed=verbose.embeds.embed_response("Your queue has finished playing.", "I will stay in the voice channel... in silence..."))
            return

        if guild_vc_data[guild_id]["queue_loop"]:
            guild_vc_data[guild_id]["guild_queue"].append(removed_song)

    await play_from_yt(message)


async def continue_to_next_req(message):
    guild_id = str(message.guild.id)

    try:
        guild_vc_data[guild_id]["voice_client"].stop()
    except AttributeError:
        await message.channel.send(embed=verbose.embeds.embed_sorry_message("I am not currently in any voice channel."))
        return

    # the "after" parameter in the voice_client.play method will take care of playing the next song


async def add_song_to_bottom_of_queue(message):
    await add_song_to_queue(message, skip_to_top=False)


async def add_song_to_top_of_queue(message):
    await add_song_to_queue(message, skip_to_top=True)


async def add_song_to_queue(message: discord.Message, skip_to_top: bool=False):
    guild_id = str(message.guild.id)
    user_song_request_list = message.content.split(" ")[3:]
    user_song_request = " ".join(user_song_request_list)

    if len(user_song_request) < 1:
        await message.channel.send(embed=verbose.embeds.embed_warning_message("No request specified."))
        return

    # Add the video metadata to queue
    # use channel.typing so the user knows something is happening - it might take a while to download metadata depending on internet speed
    async with message.channel.typing():
        if check_if_url(user_song_request, "spotify"):
            await add_spotify_playlist_to_queue(message)
            return

        with youtube_dl.YoutubeDL() as ytdl:
            if check_if_url(user_song_request, "youtube"):
                user_song_request_dict = ytdl.extract_info(
                    user_song_request, download=False)
                video_to_add = Song(youtube_metadata=user_song_request_dict)

            else:
                results = ytdl.extract_info(
                    f"ytsearch:{user_song_request}", download=False)
                if len(results['entries']) == 0:
                    await message.channel.send(embed=verbose.embeds.embed_warning_message("Sorry, I could not find a song on youtube with that name."))
                    return
                video_to_add = Song(results['entries'][0])

        if skip_to_top:
            if guild_vc_data[guild_id]["voice_client"].is_playing():
                guild_vc_data[guild_id]["guild_queue"].insert(1, video_to_add)
                await continue_to_next_req(message)
            else:
                guild_vc_data[guild_id]["guild_queue"].insert(0, video_to_add)
                await play_from_yt(message)
        
                await message.channel.send(embed=verbose.embeds.embed_successful_action(
                    f"Added [{video_to_add.name}]({video_to_add.url}) to the top of the queue."))
        else:
            guild_vc_data[guild_id]["guild_queue"].append(video_to_add)

            await message.channel.send(embed=verbose.embeds.embed_successful_action(
                f"Added [{video_to_add.name}]({video_to_add.url}) to the queue."))

            # check if voice client exists before checking if it is playing
            if guild_vc_data[guild_id]["voice_client"] and not guild_vc_data[guild_id]["voice_client"].is_playing():
                await play_from_yt(message)


async def add_spotify_playlist_to_queue(message):
    guild_id = str(message.guild.id)
    user_song_request_list = message.content.split(" ")[3:]
    user_song_request = " ".join(user_song_request_list)

    #async with message.channel.typing:
    with youtube_dl.YoutubeDL() as ytdl:
        if "playlist" in user_song_request:
            try:
                songs_to_add: list = sp.playlist_items(user_song_request, fields="items.track.name,items.track.artists.name,items.track.external_urls.spotify,total")["items"]
            except spotipy.SpotifyException:
                await message.channel.send(embed=verbose.embeds.embed_warning_message(
                    "Sorry, data could not be fetched for that playlist. Most likely it doesn't exist, it is privated, or it is too long."))
                return

            for track in songs_to_add:
                guild_vc_data[guild_id]["guild_queue"].append(
                    Song(name=f"{track['track']['name']} - {track['track']['artists'][0]['name']}", url=track['track']['external_urls']['spotify']))

                if guild_vc_data[guild_id]["voice_client"] and not guild_vc_data[guild_id]["voice_client"].is_playing():
                    await play_from_yt(message)

            await message.channel.send(embed=verbose.embeds.embed_successful_action("Playlist added to queue."))

        if "album" in user_song_request:
            try:
                songs_to_add: list = sp.album_tracks(user_song_request)["items"]
            except spotipy.SpotifyException:
                await message.channel.send(embed=verbose.embeds.embed_warning_message(
                    "Sorry, data could not be fetched for that playlist. Most likely it doesn't exist, it is privated, or it is too long."))
                return

            for track in songs_to_add:
                guild_vc_data[guild_id]["guild_queue"].append(
                    Song(name=f"{track['name']} - {track['artists'][0]['name']}", url=track['external_urls']['spotify']))

                if guild_vc_data[guild_id]["voice_client"] and not guild_vc_data[guild_id]["voice_client"].is_playing():
                    await play_from_yt(message)

            await message.channel.send(embed=verbose.embeds.embed_successful_action("Album added to queue."))

        if "track" in user_song_request:
            try:
                song_to_add: list = sp.track(user_song_request)
            except spotipy.SpotifyException:
                await message.channel.send(embed=verbose.embeds.embed_warning_message(
                    "Sorry, data could not be fetched for that playlist. Most likely it doesn't exist, it is privated, or it is too long."))
                return

            guild_vc_data[guild_id]["guild_queue"].append(
                Song(name=f"{song_to_add['name']} - {song_to_add['artists'][0]['name']}", url=song_to_add['external_urls']['spotify']))

            print("gui")
            if guild_vc_data[guild_id]["voice_client"] and not guild_vc_data[guild_id]["voice_client"].is_playing():
                await play_from_yt(message)

            await message.channel.send(embed=verbose.embeds.embed_successful_action("Song added to queue."))

        else:
            results = ytdl.extract_info(
                f"ytsearch:{user_song_request}", download=False)
            if len(results['entries']) == 0:
                await message.channel.send(embed=verbose.embeds.embed_warning_message(
                    "Sorry, robo currently only supports spotify playlists. You probably tried to request an album or track."))
                return
            video_to_add = Song(results['entries'][0])

            guild_vc_data[guild_id]["guild_queue"].append(video_to_add)
            await message.channel.send(embed=verbose.embeds.embed_successful_action(
                f"Added [{video_to_add.name}]({video_to_add.url}) to the queue."))


async def remove_from_queue(message):
    guild_id = str(message.guild.id)

    try:
        index_to_remove = int(message.content.split(" ")[3])
    except ValueError:
        await message.channel.send(embed=verbose.embeds.embed_warning_message("Must specify valid queue index."))
        return

    try:
        removed_song = guild_vc_data[guild_id]["guild_queue"].pop(index_to_remove - 1)
        await message.channel.send(
            embed=verbose.embeds.embed_successful_action(f"[{removed_song['title']}] \
                ({removed_song['webpage_url']}) has been removed from the queue"))
    except IndexError:
        await message.channel.send(embed=verbose.embeds.embed_warning_message("That queue index does not exist."))
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
    guild_id = str(message.guild.id)

    specific_queue_name = " ".join(message.content.split(" ")[3:])

    if len(specific_queue_name) > 0: # if queue specified
        guild_data = data.get_guild_data(guild_id)

        if specific_queue_name not in guild_data["saved_queues"]:
            await message.channel.send(embed=verbose.embeds.embed_warning_message("That queue does not exist."))
            return

        # load the queue of dicts and parse into Songs
        queue_to_send = [dict_to_song(song_dict) for song_dict in guild_data["saved_queues"][specific_queue_name]]

    else:
        specific_queue_name = None
        queue_to_send = guild_vc_data[guild_id]["guild_queue"]

    queue_message = QueueMessage(message, queue=queue_to_send, queue_name=specific_queue_name)

    await queue_message.send()

    if guild_vc_data[guild_id]["active_queue_message"] is not None:
        await guild_vc_data[guild_id]["active_queue_message"].clear_reactions()
    guild_vc_data[guild_id]["active_queue_message"] = queue_message


async def change_queue_page(bot_message, reaction):
    guild_id = str(bot_message.guild.id)
    if guild_id not in guild_vc_data:
        return
    if bot_message != guild_vc_data[guild_id]["active_queue_message"].message:
        return

    await guild_vc_data[guild_id]["active_queue_message"].change_page(reaction)


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
        await message.channel.send(embed=verbose.embeds.embed_warning_message("You must specify a queue to play."))
        return

    if queue_to_play not in guild_data["saved_queues"]:
        await message.channel.send(embed=verbose.embeds.embed_warning_message("That queue does not exist."))
        return

    guild_vc_data[guild_id]["guild_queue"] = [dict_to_song(song_dict) for song_dict in guild_data["saved_queues"][queue_to_play]]

    try:
        guild_vc_data[guild_id]["voice_client"].stop()
    except AttributeError:
        await message.channel.send(embed=verbose.embeds.embed_response("Queue set.", f"Type `{COMMAND_PREFIX} vc join` to start listening."))
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

    queue_to_save = [song_to_dict(song) for song in guild_vc_data[guild_id]["guild_queue"]]

    queue_name = " ".join(message.content.split(" ")[3:])
    guild_data = data.get_guild_data(guild_id)
    guild_data["saved_queues"][queue_name] = queue_to_save
    data.set_guild_data(guild_id, guild_data)

    await message.channel.send(embed=verbose.embeds.embed_successful_action(
        f"Saved current queue preset as `{queue_name}`"))


def song_to_dict(song: Song) -> dict:
    song_dict = {}
    song_dict["name"] = song.name
    song_dict["url"] = song.url
    song_dict["youtube_metadata"] = song.youtube_metadata

    return song_dict


def dict_to_song(song_dict: dict) -> Song:
    if song_dict["youtube_metadata"] != {}:
        song = Song(youtube_metadata=song_dict["youtube_metadata"])
    else:
        song = Song(name=song_dict["name"], url=song_dict["url"])

    return song


async def shuffle_queue(message):
    guild_id = str(message.guild.id)
    if guild_vc_data[guild_id]["voice_client"].is_playing():
        playing_song = guild_vc_data[guild_id]["guild_queue"].pop(0)
        random.shuffle(guild_vc_data[guild_id]["guild_queue"])
        guild_vc_data[guild_id]["guild_queue"].insert(0, playing_song)

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


async def toggle_queue_loop(message):
    guild_id = str(message.guild.id)

    if guild_vc_data[guild_id]["queue_loop"]:
        guild_vc_data[guild_id]["queue_loop"] = False
        await message.channel.send(embed=verbose.embeds.embed_response_without_title_custom_emote("Queue loop disabled.", ":repeat:"))
    else:
        guild_vc_data[guild_id]["queue_loop"] = True
        await message.channel.send(embed=verbose.embeds.embed_response_without_title_custom_emote("Queue loop enabled.", ":repeat:"))


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


def check_if_url(string, website):
    return (string.startswith("http") or string.startswith("www")) and (website in string)


COMMAND_HANDLER_DICT = {
    "join": join_voice_channel,
    "leave": leave_voice_channel,
    "add": add_song_to_bottom_of_queue,
    "playnow": add_song_to_top_of_queue,
    "skip": continue_to_next_req,
    "queue": send_queue,
    "remove": remove_from_queue,
    "save-queue": save_queue,
    "shuffle": shuffle_queue,
    "queue-list": send_queue_list,
    "play-queue": play_queue,
    "toggle-np": toggle_np,
    "loop": toggle_loop,
    "loop-queue": toggle_queue_loop,
}
