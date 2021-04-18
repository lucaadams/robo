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
    # if no second parameter specified, reply on discord
    except:
        message.channel.send(embed = text_module.embed_error_message("Invalid command."))
        return
    
    if second_parameter == "join":
        try_join_vc = await join_voice_channel(message)
        # if bot is already in a vc, do nothing
        if try_join_vc != None:
            guild_vc_dict[guild_id]["voice_client"] = try_join_vc

    elif second_parameter == "leave":
        # checks if bot is in a vc, if not then reply on discord
        if not guild_vc_dict[guild_id]["voice_client"].is_connected():
            await message.channel.send(embed = await text_module.embeds.embed_response("Sorry, I couldn't complete that.", "I am not currently in any voice channel."))
        await guild_vc_dict[guild_id]["voice_client"].disconnect()


async def join_voice_channel(message):
    try:
        channel = message.author.voice.channel
    # if user not in a vc, catch error and reply on discord
    except:
        await message.channel.send(embed = await text_module.embeds.embed_response("Sorry, I couldn't complete that.",  "You must be in a voice channel to use this command."))
        return None
    try:
        return await channel.connect()
    # if already in a channel, catch error and reply on discord
    except discord.errors.ClientException:
        await message.channel.send(embed = await text_module.embeds.embed_response("Sorry, I couldn't complete that.", "I am already in a voice channel."))
        return None

