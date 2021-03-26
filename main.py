import discord
import json
import os


# constants
command_prefix = ("!robo")
token = os.getenv("TOKEN")
client = discord.Client()

with open("keywords.json", "r") as keywords_file:
    keywords_dictionary = {}
    keywords_dictionary = json.loads(keywords_file.read())


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

        await save_keywords()

    elif message_split == "remove":
        print ("done")
        message_removal = message.content.split(" ")[2]
        keywords_dictionary.pop(message_removal)
        await message.channel.send("Keyword removed.")

# save keywords to file
async def save_keywords():
    keywords_json = json.dumps(keywords_dictionary)
    with open ("keywords.json", "w") as keywords_file:
        keywords_file.write(keywords_json)


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



#keep at end
client.run(token)
