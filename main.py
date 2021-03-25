import discord
import json


# constants
token = "ODI0MzQwOTI2MTAwNzk5NTM4.YFt9UA.VmABEAOFXUx9fEUnkpOz27Ix2eM"
command_prefix = "!robo"

client = discord.Client()

keywords_dictionary = {}

@client.event
async def on_ready():
    print("logged on")


# command manager
async def execute_command(message):
    message_split = message.content.split(" ")[1]
    
    if message_split == "add":
        message_addition = message.content.split(" ")[2]
        message_value = " ".join(message.content.split(" ")[3:])
        keywords_dictionary[message_addition] = message_value
        await message.channel.send("Keyword added.")

    elif message_split == "remove":
        print ("done")
        message_removal = message.content.split(" ")[2]
        keywords_dictionary.pop(message_removal)
        await message.channel.send("Keyword removed.")


# recieve message
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith(command_prefix):
        await execute_command(message)
        return

    for keyword in keywords_dictionary.keys():
        if message.content.__contains__(keyword):
            await message.channel.send(keywords_dictionary[keyword])
            return

    if message.content.startswith("hey"):
        name = message.content.split(" ") 
        await message.channel.send(f"Hey {name[1]}!")



#keep at end
client.run(token)
