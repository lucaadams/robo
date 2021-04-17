import os
import time
import discord
import json

import image_commands.quote_functions
import text_commands.keyword_functions
import text_commands.embeds
import game_commands.counting
import game_commands.game_functions


# constants
COMMAND_PREFIX = ("!robo")
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
client = discord.Client()


@client.event
async def on_ready():
    print("logged on")
    await client.change_presence(activity=discord.Game(name="!robo help"))


# command manager
async def execute_command(guild_id, message):
    try:
        first_parameter = message.content.split(" ")[1]
    except:
        await message.channel.send(embed=await text_commands.embeds.embed_error_message("Command not recognised. Type !robo help for a list of commands. "))
        return

    if first_parameter == "add":
        await text_commands.keyword_functions.add(guild_id, message, message.content.split(" ")[2], " ".join(message.content.split(" ")[3:]))

    elif first_parameter == "remove":
        try:
            await text_commands.keyword_functions.remove(guild_id, message, message.content.split(" ")[2])
        except:
            await message.channel.send(embed=await text_commands.embeds.embed_error_message("That keyword does not exist. Did you make a typo? "))

    elif first_parameter == "edit":
        try:
            if message.content.split(" ")[3] == "":
                await message.channel.send(embed=await text_commands.embeds.embed_error_message("Name of new keyword must be specified. "))
            else:
                await text_commands.keyword_functions.edit(guild_id, message, message.content.split(" ")[2], " ".join(message.content.split(" ")[3:]))
        except:
            await message.channel.send(embed=await text_commands.embeds.embed_error_message("That keyword does not exist. Did you make a typo? "))

    elif first_parameter == "list":
        await text_commands.keyword_functions.list(guild_id, message)

    elif first_parameter == "quote":
        await image_commands.quote_functions.execute_quote_command(message)

    elif first_parameter == "games":
        await game_commands.game_functions.start_game(guild_id, message)

    elif first_parameter == "help":
        await command_help(message)

    elif first_parameter == "echo":
        await message.channel.send(embed=await text_commands.embeds.embed_response("Your message was: ", " ".join(message.content.split(" ")[2:])))

    elif first_parameter == "ping":
        await message.channel.send("Pong!")

    elif first_parameter == "nuke":
        await message.channel.send(embed=await text_commands.embeds.embed_response("Server nuke engaged. 20 second countdown initiated.", 'To cance, type "!robo cancel nuke"'))
        for i in range(20, 0, -1):
            time.sleep(1)
            await message.channel.send(i)
        await message.channel.send(embed=await text_commands.embeds.embed_error_message("Server nuke failed. Please try again later. "))

    else:
        await message.channel.send(embed=await text_commands.embeds.embed_error_message("Command not recognised. Type !robo help for a list of commands. "))


# command help list
async def command_help(message):
    await message.channel.send(embed=await text_commands.embeds.embed_response("Commands:", '''Here is a list of the commands you can use: 
    • `!robo add [keyword] [value]` 
    • `!robo remove [keyword]` 
    • `!robo edit [old keyword] [new keyword]` 
    • `!robo list` 
    • `!robo quote [image type] "[quote message]" "[quote author]"`
    • `!robo games [game (e.g. counting)]`'''))


# recieve message
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    await game_commands.counting.check_message(message)

    guild_id = str(message.guild.id)

    if message.content.startswith(COMMAND_PREFIX):
        await execute_command(guild_id, message)
        return

    await text_commands.keyword_functions.check_keywords(guild_id, message)


# keep at end
client.run(TOKEN)

