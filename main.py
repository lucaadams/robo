import discord
import json
import os

import embeds
import keyword_functions


# constants
COMMAND_PREFIX = ("!robo")
TOKEN = os.getenv("TOKEN")
client = discord.Client()


@client.event
async def on_ready():
    print("logged on")


# command manager
async def execute_command(message):
    first_parameter = message.content.split(" ")[1]

    if first_parameter == "add":
        await keyword_functions.add(message, message.content.split(" ")[2], " ".join(message.content.split(" ")[3:]))

    elif first_parameter == "remove":
        await keyword_functions.remove(message, message.content.split(" ")[2])

    elif first_parameter == "list":
        await keyword_functions.list(message)

    elif first_parameter == "help":
        await command_help(message)

    else:
        await message.channel.send(embed=await embeds.embed_error_message(":exclamation: Command not recognised. Type !robo help for a list of commands. "))


# command help list
async def command_help(message):
    await message.channel.send(embed=await embeds.embed_response("Commands:", "Here is a list of the commands you can use: \n• `!robo add [keyword] [value]` \n• `!robo remove [keyword]` \n• `!robo list`"))


# recieve message
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith(COMMAND_PREFIX):
        await execute_command(message)
        return

    await keyword_functions.check_keywords(message)


# keep at end
client.run(TOKEN)

