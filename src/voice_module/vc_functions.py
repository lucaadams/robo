import time
import tempfile
import youtube_dl
import discord
from discord.ext import commands
import youtube_dl
import json

import text_module.embeds

guild_vc_dict = {}

temp_file = tempfile.mkdtemp()

async def vc_command_handler(message):
    guild_id = message.guild.id
    if guild_id not in guild_vc_dict:
        guild_vc_dict[guild_id] = {}
    if "guild_queue" not in guild_vc_dict[guild_id]:
        guild_vc_dict[guild_id]["guild_queue"] = []

    try:
        second_parameter = message.content.split(" ")[2]
    # if no second parameter specified, send error message
    except:
        await message.channel.send(embed=await text_module.embeds.embed_error_message("Incomplete command."))
        return

    if second_parameter == "join":
        voice_client = await join_voice_channel(message)
        if voice_client != None:
            guild_vc_dict[guild_id]["voice_client"] = voice_client

        await continue_to_next_request(message, guild_vc_dict)

    elif second_parameter == "leave":
        # checks if bot is in a vc, if not then reply on discord
        try:
            if not guild_vc_dict[guild_id]["voice_client"].is_connected():
                await message.channel.send(embed=await text_module.embeds.embed_sorry_message("I am not currently in any voice channel."))
            await guild_vc_dict[guild_id]["voice_client"].disconnect()
        # catch error if there is no key "voice client" in guild_vc_dict. This only happens when user tries to get bot to leave before having asked them to join.
        except KeyError:
            await message.channel.send(embed=await text_module.embeds.embed_sorry_message("I am not currently in any voice channel."))

    elif second_parameter == "play":
        if len(message.content.split(" ")) >= 4:
            user_song_request = " ".join(message.content.split()[3:])
        else:
            await message.channel.send(embed=await text_module.embeds.embed_error_message("No link specified."))
            return
            #user_song_request = "https://www.youtube.com/watch?v=_37GPQT_qpc"

        try:
            voice_client = guild_vc_dict[guild_id]["voice_client"]
        except:
            await message.channel.send(embed=await text_module.embeds.embed_sorry_message("I am not currently in any voice channel. Please type `!robo vc join`."))
            return
        
        timestamp = time.time()

        youtube_dl_opts = {
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': temp_file + '/' + str(timestamp) + '-%(title)s-%(id)s'
        }

        with youtube_dl.YoutubeDL(youtube_dl_opts) as ytdl:
            metadata = ytdl.extract_info(
                user_song_request, download=True)
            file_path = str(f"{temp_file}/{timestamp}-{metadata['title']}-{metadata['id']}.mp3")

        #await message.channel.send(embed=await text_module.embeds.youtube_info(metadata))

        voice_client.play(discord.FFmpegPCMAudio(
            executable="ffmpeg", source=file_path))


async def join_voice_channel(message):
    try:
        channel = message.author.voice.channel
    # if user not in a vc, catch error and reply on discord
    except:
        await message.channel.send(embed=await text_module.embeds.embed_sorry_message("You must be in a voice channel to use this command."))
        return None
    try:
        return await channel.connect()
    # if already in a channel, catch error and reply on discord
    except discord.errors.ClientException:
        await message.channel.send(embed=await text_module.embeds.embed_sorry_message("I am already in a voice channel."))
        return None


async def continue_to_next_request(message, guild_vc_dict):
    guild_id = message.guild.id
    guild_vc_data = guild_vc_dict[guild_id]

    try:
        check_if_connected = guild_vc_data["voice_client"].is_connected()
    except:
        check_if_connected = False

    if len(guild_vc_data["guild_queue"]) != 0 and check_if_connected:
        guild_player = await guild_vc_data["voice_client"].create_ytdl_player(guild_vc_data["guild_queue"][0])
        guild_player.play()

