import os
import time
import asyncio
import discord
import traceback
import logging

import verbose.embeds
import modules.image.quote_functions
import modules.text.keyword_functions
import modules.games.counting
import modules.games.game_functions
import modules.voice.vc_functions
import modules.minecraft.minecraft_functions
import modules.minecraft.hypixel
import modules.flashcards.flashcard_functions
from modules.flashcards.flashcard_functions import flashcard_data
import modules.help.help_functions


COMMAND_PREFIX = os.getenv("ROBO_COMMAND_PREFIX") or "!robo"
CLIENT = discord.Client()
application_info = None
stop_emoji = "⏹️"


def run_client():
    token = os.getenv("DISCORD_BOT_TOKEN")
    if token is None:
        logging.warn("The DISCORD_BOT_TOKEN environment variable has no value.")
        while not token:
            token = input("Enter token > ")
    CLIENT.run(token)


@CLIENT.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send(embed=verbose.embeds.embed_response_custom_emote(
                "Hey, I'm Robo!", f"_I'm a Discord bot written in Python using the Discord.py rewrite, currently in {len(CLIENT.guilds)} servers._\n \
                - [link to github](https://github.com/lucaadams/robo) - \n \
                    To get started, type `{COMMAND_PREFIX} help`.", ":wave:"))
            break


@CLIENT.event
async def on_ready():
    global application_info
    application_info = await CLIENT.application_info()
    await CLIENT.change_presence(activity=discord.Game(name=f"{COMMAND_PREFIX} help"))
    logging.info("Client ready")


@CLIENT.event
async def on_error(event, *args):
    err = traceback.format_exc()
    logging.warning(err)
    await application_info.owner.send(embed=verbose.embeds.embed_error_message(f"```{err}```"), delete_after=3600)


# recieve message
@CLIENT.event
async def on_message(message):
    if message.author == CLIENT.user:
        return

    guild_id = str(message.guild.id)

    if message.content.startswith(COMMAND_PREFIX):
        await execute_command(message)
        return

    await modules.games.counting.check_message(message)

    if guild_id in flashcard_data:
        if flashcard_data[guild_id]["flashcard_creation_in_progress"] and \
            message.author == flashcard_data[guild_id]["user"] and message.channel == flashcard_data[guild_id]["channel"] and \
                len(message.content.split('"')) == 5:
            await modules.flashcards.flashcard_functions.add_flashcard_to_set(message)
            await message.add_reaction("✅")

    await modules.text.keyword_functions.check_keywords(guild_id, message)


@CLIENT.event
async def on_reaction_add(reaction, user):
    # if the reaction was added by the bot, return
    if user == CLIENT.user:
        return

    bot_message = reaction.message

    # if the reaction is not on the bot's own message, return
    if bot_message.author != CLIENT.user:
        return
    
    await reaction.remove(user)

    # if the reaction is not meant for a module it will just return and do nothing
    await modules.minecraft.hypixel.change_page(bot_message, reaction)
    await modules.flashcards.flashcard_functions.use_flashcards(bot_message, reaction)


# command manager
async def execute_command(message):
    try:
        first_parameter = message.content.split(" ")[1]
    except IndexError:
        await message.channel.send(embed=verbose.embeds.embed_response_custom_emote(
            "Hi, I'm Robo!", 
            f"_I'm a Discord bot written in Python using the Discord.py rewrite, currently in {len(CLIENT.guilds)} servers._\n \
            - [link to github](https://github.com/lucaadams/robo) - \n \
                To view a list of commands, type `{COMMAND_PREFIX} help`.", ":wave:"))
        return

    if first_parameter == "keyword" or first_parameter == "k":
        await modules.text.keyword_functions.command_handler(message)

    elif first_parameter == "quote":
        await modules.image.quote_functions.execute_quote_command(message)

    elif first_parameter == "games":
        await modules.games.game_functions.start_game(message)

    elif first_parameter == "vc":
        await modules.voice.vc_functions.vc_command_handler(message)

    elif first_parameter == "minecraft" or first_parameter == "mc":
        await modules.minecraft.minecraft_functions.minecraft_command_handler(message)

    elif first_parameter == "flashcards":
        await modules.flashcards.flashcard_functions.flashcard_command_handler(message)

    elif first_parameter == "help":
        await modules.help.help_functions.help_message_handler(message, COMMAND_PREFIX)

    elif first_parameter == "echo":
        await message.channel.send(embed=verbose.embeds.embed_response("Your message was: ", " ".join(message.content.split(" ")[2:])))

    elif first_parameter == "ping":
        ping_start = time.time()
        await message.channel.send("Pong!")
        ping_end = time.time()
        await message.channel.send(embed=verbose.embeds.embed_response_without_title_custom_emote(
            f"That was about {int((ping_end - ping_start) * 1000)}ms.", ":stopwatch:"))

    elif first_parameter == "nuke":
        await message.channel.send(embed=verbose.embeds.embed_response(
            "Server nuke engaged. 20 second countdown initiated.", 
            f'To cancel, type "{COMMAND_PREFIX} cancel nuke"'))
        for i in range(20, 0, -1):
            asyncio.sleep(1)
            await message.channel.send(i)
        await message.channel.send(embed=verbose.embeds.embed_error_message("Server nuke failed. Please try again later. "))

    else:
        await message.channel.send(embed=verbose.embeds.embed_error_message(
            f"Command not recognised. Type `{COMMAND_PREFIX} help` for a list of commands. "))
