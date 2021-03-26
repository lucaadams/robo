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
        message_addition = message.content.split(" ")[2]
        await keyword_functions.add(message, first_parameter, message_addition)

    elif first_parameter == "remove":
        await keyword_functions.remove(message, first_parameter)

    elif first_parameter == "list":
        await keyword_functions.list(message, first_parameter)

    else:
        await message.channel.send(embed=await embeds.embed_error_message(":exclamation: Keyword not recognised. Did you make a typo? "))


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
