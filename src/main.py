import os
import time
import discord
import json
import logging

import image_module.quote_functions
import text_module.keyword_functions
import text_module.embeds
import games_module.counting
import games_module.game_functions
import voice_module.vc_functions
import help_module.help_functions

# constants
COMMAND_PREFIX = ("!robo")
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
client = discord.Client()


@client.event
async def on_ready():
    logging.log(logging.INFO, "Client ready")
    await client.change_presence(activity=discord.Game(name="!robo help"))


# command manager
async def execute_command(guild_id, message):
    try:
        first_parameter = message.content.split(" ")[1]
    except:
        await message.channel.send(embed=text_module.embeds.embed_error_message("Command not recognised. Type !robo help for a list of module. "))
        return

    if first_parameter == "add":
        await text_module.keyword_functions.add(guild_id, message, message.content.split(" ")[2], " ".join(message.content.split(" ")[3:]))

    elif first_parameter == "remove":
        try:
            await text_module.keyword_functions.remove(guild_id, message, message.content.split(" ")[2])
        except:
            await message.channel.send(embed=text_module.embeds.embed_error_message("That keyword does not exist. Did you make a typo? "))

    elif first_parameter == "edit":
        try:
            if message.content.split(" ")[3] == "":
                await message.channel.send(embed=text_module.embeds.embed_error_message("Name of new keyword must be specified. "))
            else:
                await text_module.keyword_functions.edit(guild_id, message, message.content.split(" ")[2], " ".join(message.content.split(" ")[3:]))
        except:
            await message.channel.send(embed=text_module.embeds.embed_error_message("That keyword does not exist. Did you make a typo? "))

    elif first_parameter == "list":
        await text_module.keyword_functions.list(guild_id, message)

    elif first_parameter == "quote":
        await image_module.quote_functions.execute_quote_command(message)

    elif first_parameter == "games":
        await games_module.game_functions.start_game(guild_id, message)

    elif first_parameter == "vc":
        await voice_module.vc_functions.vc_command_handler(message)

    elif first_parameter == "help":
        await help_module.help_functions.help_message_handler(message, COMMAND_PREFIX)

    elif first_parameter == "echo":
        await message.channel.send(embed=text_module.embeds.embed_response("Your message was: ", " ".join(message.content.split(" ")[2:])))

    elif first_parameter == "ping":
        ping_start = time.time()
        await message.channel.send("Pong!")
        ping_end = time.time()
        await message.channel.send(embed=text_module.embeds.embed_response_without_title_custom_emote(f"That was about {int((ping_end - ping_start) * 1000)}ms.", ":stopwatch:"))

    elif first_parameter == "nuke":
        await message.channel.send(embed=text_module.embeds.embed_response("Server nuke engaged. 20 second countdown initiated.", 'To cancel, type "!robo cancel nuke"'))
        for i in range(20, 0, -1):
            time.sleep(1)
            await message.channel.send(i)
        await message.channel.send(embed=text_module.embeds.embed_error_message("Server nuke failed. Please try again later. "))

    else:
        await message.channel.send(embed=text_module.embeds.embed_error_message("Command not recognised. Type !robo help for a list of commands. "))


# recieve message
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    await games_module.counting.check_message(message)

    guild_id = str(message.guild.id)

    if message.content.startswith(COMMAND_PREFIX):
        await execute_command(guild_id, message)
        return

    await text_module.keyword_functions.check_keywords(guild_id, message)


# keep at end
logging.basicConfig(level=logging.INFO)
client.run(TOKEN)
