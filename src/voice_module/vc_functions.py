import asyncio
import youtube_dl
import pafy
import discord

import bot
import data
import text_module.embeds

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
    'guild_queue': [], 'loop': False, 'already_skipped': False, 'enable_np': True
}

guild_vc_dict = {}


async def vc_command_handler(message):
    guild_id = str(message.guild.id)
    if guild_id not in guild_vc_dict:
        guild_vc_dict[guild_id] = DEFAULT_GUILD_VC_DATA.copy()

    guild_queue = guild_vc_dict[guild_id]["guild_queue"]

    try:
        second_parameter = message.content.split(" ")[2]
    # if no second parameter specified, send error message
    except IndexError:
        await message.channel.send(embed=text_module.embeds.embed_error_message("Incomplete command."))
        return

    if second_parameter == "join":
        voice_client = await join_voice_channel(message)
        if voice_client is None:
            return
            
        guild_vc_dict[guild_id]["voice_client"] = voice_client

        await play_from_yt(guild_vc_dict, message)

    elif second_parameter == "leave":
        # checks if bot is in a vc, if not then reply on discord
        try:
            if not guild_vc_dict[guild_id]["voice_client"].is_connected():
                await message.channel.send(embed=text_module.embeds.embed_sorry_message("I am not currently in any voice channel."))
            await guild_vc_dict[guild_id]["voice_client"].disconnect()
        # catch error if there is no key "voice client" in guild_vc_dict. This only happens when user tries to get bot to leave before having asked them to join.
        except KeyError:
            await message.channel.send(embed=text_module.embeds.embed_sorry_message("I am not currently in any voice channel."))

    elif second_parameter == "add":
        user_song_request_list = message.content.split(" ")[3:]
        user_song_request = " ".join(user_song_request_list)
        if len(user_song_request) < 1:
            await message.channel.send(embed=text_module.embeds.embed_error_message("No request specified."))
            return

        # Add the video metadata to queue
        async with message.channel.typing():
            with youtube_dl.YoutubeDL() as ytdl:
                if check_if_url(user_song_request):
                    user_song_request_dict = ytdl.extract_info(user_song_request, download=False)
                    video_to_add = user_song_request_dict
                else:
                    user_song_request_dict = ytdl.extract_info(f"ytsearch:{user_song_request}", download=False)
                    video_to_add = user_song_request_dict['entries'][0]
            
            guild_queue.append(video_to_add)

        await message.channel.send(embed=text_module.embeds.embed_successful_action(
            f"Added [{video_to_add['title']}]({video_to_add['webpage_url']}) to the queue"))

    elif second_parameter == "skip" or second_parameter == "next":
        try:
            guild_vc_dict[guild_id]["voice_client"].stop()
        except KeyError:
            await message.channel.send(embed=text_module.embeds.embed_sorry_message("I am not currently in any voice channel."))
            return

        try:
            guild_vc_dict[guild_id]["guild_queue"].pop(0)
            guild_vc_dict[guild_id]["already_skipped"] = True
        except IndexError:
            await message.channel.send(embed=text_module.embeds.embed_error_message("Queue is currently empty."))
            return

        await play_from_yt(guild_vc_dict, message)

    elif second_parameter == "loop":
        if guild_vc_dict[guild_id]["loop"]:
            guild_vc_dict[guild_id]["loop"] = False
            await message.channel.send(embed=text_module.embeds.embed_response_without_title_custom_emote("Loop disabled.", ":repeat:"))
        else:
            guild_vc_dict[guild_id]["loop"] = True
            await message.channel.send(embed=text_module.embeds.embed_response_without_title_custom_emote("Loop enabled.", ":repeat:"))

    elif second_parameter == "queue":
        desc = ""
        num = 1
        for metadata in guild_vc_dict[guild_id]["guild_queue"]:
            desc += f"{num} - [{metadata['title']}]({metadata['webpage_url']})\n"
            num += 1
        if desc == "":
            await message.channel.send(embed=text_module.embeds.embed_response_without_title("Your queue is currently empty."))
        else:
            await message.channel.send(embed=text_module.embeds.embed_response("Up next", desc))

    elif second_parameter == "remove":
        try:
            index_to_remove = int(message.content.split(" ")[3])
        except ValueError:
            await message.channel.send(embed=text_module.embeds.embed_error_message("Must specify valid queue index."))
            return

        try:
            await message.channel.send(
                embed=text_module.embeds.embed_successful_action(f"[{guild_vc_dict[guild_id]['guild_queue'][index_to_remove - 1]['title']}]({guild_vc_dict[guild_id]['guild_queue'][index_to_remove - 1]['webpage_url']}) \
                    has been removed from the queue"))
            guild_queue.pop(index_to_remove - 1)
        except IndexError:
            await message.channel.send(embed=text_module.embeds.embed_error_message("That queue index does not exist."))
            return

        if index_to_remove == 1:
            try:
                guild_vc_dict[guild_id]["voice_client"].stop()
            except AttributeError or KeyError:
                return

            guild_vc_dict[guild_id]["already_skipped"] = True
            
            await play_from_yt(guild_vc_dict, message)

    elif second_parameter == "toggle-np":
        if guild_vc_dict[guild_id]["enable_np"]:
            guild_vc_dict[guild_id]["enable_np"] = False
            await message.channel.send(embed=text_module.embeds.embed_response_without_title_custom_emote("'Now playing' message disabled.", ":ok_hand:"))
        else:
            guild_vc_dict[guild_id]["ensable_np"] = True
            await message.channel.send(embed=text_module.embeds.embed_response_without_title_custom_emote("'Now playing' message enabled.", ":ok_hand:"))

    elif second_parameter == "save-queue":
        queue_name = " ".join(message.content.split(" ")[3:])
        guild_data = data.get_guild_data(guild_id)
        guild_data["saved_queues"][queue_name] = guild_queue.copy()
        data.set_guild_data(guild_id, guild_data)

    elif second_parameter == "queue-list":
        guild_data = data.get_guild_data(guild_id)
        desc = ""
        for queue_name in guild_data["saved_queues"]:
            desc += f"- `{queue_name}`"
        if desc == "":
            await message.channel.send(embed=text_module.embeds.embed_response_without_title("You don't currently have any saved queues."))
        else:
            await message.channel.send(embed=text_module.embeds.embed_response("Saved queues:", desc))

    elif second_parameter == "play-queue":
        queue_to_play = message.content.split(" ")[3]
        guild_data = data.get_guild_data(guild_id)
        if queue_to_play not in guild_data["saved_queues"]:
            return
            
        guild_vc_dict[guild_id]["guild_queue"] = guild_data["saved_queues"][queue_to_play]

        print(guild_vc_dict[guild_id]["guild_queue"])
        print(guild_queue)

        try:
            guild_vc_dict[guild_id]["voice_client"].stop()
        except KeyError:
            await message.channel.send(embed=text_module.embeds.embed_sorry_message("I am not currently in any voice channel."))
            return

        await play_from_yt(guild_vc_dict, message)

    else:
        await message.channel.send(embed=text_module.embeds.embed_error_message("Invalid command."))


async def join_voice_channel(message):
    try:
        channel = message.author.voice.channel
    # if user not in a vc, catch error and reply on discord
    except AttributeError:
        await message.channel.send(embed=text_module.embeds.embed_sorry_message("You must be in a voice channel to use this command."))
        return None
    try:
        return await channel.connect()
    # if already in a channel, catch error and reply on discord
    except discord.errors.ClientException:
        await message.channel.send(embed=text_module.embeds.embed_sorry_message("I am already in a voice channel."))
        return None


async def play_from_yt(guild_vc_dict, message):
    guild_id = str(message.guild.id)
    guild_queue = guild_vc_dict[guild_id]["guild_queue"]

    try:
        song_request_metadata = guild_queue[0]
    except IndexError:
        await message.channel.send(embed=text_module.embeds.embed_response("The queue is empty.", "I will stay in the voice channel... in silence..."))
        return

    voice_client = guild_vc_dict[guild_id]["voice_client"]

    audio = pafy.new(song_request_metadata['id'], ydl_opts=YOUTUBE_DL_OPTIONS).getbestaudio()
    voice_client.play(discord.FFmpegPCMAudio(
        audio.url, options=FFMPEG_OPTIONS), after=lambda e: asyncio.run_coroutine_threadsafe(on_playback_finished(guild_vc_dict, message), bot.CLIENT.loop))

    if guild_vc_dict[guild_id]["enable_np"]:
        await message.channel.send(embed=text_module.embeds.embed_youtube_info(song_request_metadata))


async def on_playback_finished(guild_vc_dict, message):
    guild_id = str(message.guild.id)

    if not guild_vc_dict[guild_id]["loop"] and not guild_vc_dict[guild_id]["already_skipped"]:
        try:
            guild_vc_dict[guild_id]["guild_queue"].pop(0)
        except:
            await message.channel.send(embed=text_module.embeds.embed_response("Your queue has finished playing.", "I will stay in the voice channel... in silence..."))
    
    guild_vc_dict[guild_id]["already_skipped"] = False

    await play_from_yt(guild_vc_dict, message)


def check_if_url(string):
    return string.startswith("http") or string.startswith("www")
