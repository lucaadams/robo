import discord
from discord.ext import commands

import text_module.embeds

guild_vc_dict = {}


async def vc_command_handler(message):
    guild_id = message.guild.id
    if guild_id not in guild_vc_dict:
        guild_vc_dict[guild_id] = {}

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

    elif second_parameter == "leave":
        # checks if bot is in a vc, if not then reply on discord
        try:
            if not guild_vc_dict[guild_id]["voice_client"].is_connected():
                await message.channel.send(embed=await text_module.embeds.embed_sorry_message("I am not currently in any voice channel."))
            await guild_vc_dict[guild_id]["voice_client"].disconnect()
        # catch error if there is no key "voice client" in guild_vc_dict. This only happens when user tries to get bot to leave before having asked them to join.
        except KeyError:
            await message.channel.send(embed=await text_module.embeds.embed_sorry_message("I am not currently in any voice channel."))


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
