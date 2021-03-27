import discord
import json

import embeds


with open("keywords.json", "r") as keywords_file:
    keywords_dictionary = json.loads(keywords_file.read())


async def add(message, keyword, value):
    keywords_dictionary[keyword] = value
    await message.channel.send(embed = await embeds.embed_successful_action("Keyword added. "))

    await save_keywords()

async def remove(message, keyword):
    message_removal = message.content.split(" ")[2]
    keywords_dictionary.pop(message_removal)
    await message.channel.send(embed = await embeds.embed_successful_action("Keyword removed. "))

async def edit(message, old_keyword, new_keyword):
    keywords_dictionary[new_keyword] = keywords_dictionary.pop(old_keyword)
    await message.channel.send(embed = await embeds.embed_successful_action("Keyword edited. "))

    await save_keywords()

async def list(message):
    keywords_list = ""
    for keyword in keywords_dictionary:
        keywords_list += f"• `{keyword} - {keywords_dictionary[keyword]}`\n"
    await message.channel.send(embed = await embeds.embed_response("Keywords:", f"{keywords_list}"))


# save keywords to file
async def save_keywords():
    keywords_json = json.dumps(keywords_dictionary)
    with open("keywords.json", "w") as keywords_file:
        keywords_file.write(keywords_json)


async def check_keywords(message):
    for keyword in keywords_dictionary.keys():
            if message.content.__contains__(keyword):
                await message.channel.send(keywords_dictionary[keyword])
                return

