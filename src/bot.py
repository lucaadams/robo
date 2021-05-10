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

COMMAND_PREFIX = os.getenv("ROBO_COMMAND_PREFIX") or "!robo"
CLIENT = discord.Client()


def run_client():
    token = os.getenv("DISCORD_BOT_TOKEN")
    if token == None:
        logging.log(
            logging.WARN, "The DISCORD_BOT_TOKEN environment variable has no value.")
        while not token:
            token = input("Enter token > ")
    CLIENT.run(token)


@CLIENT.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send(embed=text_module.embeds.embed_response_custom_emote("Hey, I'm Robo!", f"_I'm a Discord bot written in Python using the Discord.py rewrite._\n \
                - [link to github](https://github.com/lucaadams/robo) - \n \
                    To get started, type `{COMMAND_PREFIX} help`.", ":wave:"))
            break


@CLIENT.event
async def on_ready():
    logging.log(logging.INFO, " Test client ready")
    await CLIENT.change_presence(activity=discord.Game(name=f"{COMMAND_PREFIX} help"))


# recieve message
@CLIENT.event
async def on_message(message):
    if message.author == CLIENT.user:
        return

    await games_module.counting.check_message(message)

    guild_id = str(message.guild.id)

    if message.content.startswith(COMMAND_PREFIX):
        await execute_command(guild_id, message)
        return

    await text_module.keyword_functions.check_keywords(guild_id, message)


# command manager
async def execute_command(guild_id, message):
    try:
        first_parameter = message.content.split(" ")[1]
    except:
        await message.channel.send(embed=text_module.embeds.embed_response_custom_emote("Hi, I'm Robo!", f"_I'm a Discord bot written in Python using the Discord.py rewrite._\n \
            - [link to github](https://github.com/lucaadams/robo) - \n \
                To view a list of commands, type `{COMMAND_PREFIX} help`.", ":wave:"))
        return

    if first_parameter == "keyword" or first_parameter == "k":
        await text_module.keyword_functions.command_handler(message)

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
        await message.channel.send(embed=text_module.embeds.embed_response("Server nuke engaged. 20 second countdown initiated.", f'To cancel, type "{COMMAND_PREFIX} cancel nuke"'))
        for i in range(20, 0, -1):
            time.sleep(1)
            await message.channel.send(i)
        await message.channel.send(embed=text_module.embeds.embed_error_message("Server nuke failed. Please try again later. "))

    else:
        await message.channel.send(embed=text_module.embeds.embed_error_message(f"Command not recognised. Type `{COMMAND_PREFIX} help` for a list of commands. "))
