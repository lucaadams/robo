import requests
from base64 import b64decode
import json
import logging
import discord

import verbose.embeds
import cache


SUCCESSFUL_STATUS_CODE = 200

get_uuid_url = "https://api.mojang.com/users/profiles/minecraft/{}"
get_user_info_url = "https://sessionserver.mojang.com/session/minecraft/profile/{}"

recent_searches = cache.Cache()


async def get_user_skin(message):
    try:
        username = message.content.split()[3].lower()
    except IndexError:
        await message.channel.send(embed=verbose.embeds.embed_error_message(f"You must specify a user."))
        return


    # only send request if user info is not in cache
    if username in recent_searches.object_keys():
        user_info = recent_searches.get_object(username)
    else:
        # first send request for the UUID of USER, then send request using that UUID to get more data including skin url
        uuid_request = requests.get(url = get_uuid_url.format(username))

        if uuid_request.status_code != SUCCESSFUL_STATUS_CODE:
            await message.channel.send(embed=verbose.embeds.embed_sorry_message(f"I could not find a user with the name `{username}`. Please check spelling and try again."))
            return
        
        uuid = uuid_request.json()["id"]

        user_info_request = requests.get(url = get_user_info_url.format(uuid))

        logging.info("Request successfully sent to mojang api")

        user_info = user_info_request.json()
        object_to_cache = cache.CachedObject(username, user_info)
        recent_searches.add(object_to_cache)

    # search properties for the "textures" property where i can get the user's skin
    for property in user_info["properties"]:
        if property["name"] == "textures":
            # decode skin code from Base64 to return a json file with user textures
            # `property["value"]` is the value of the textures property
            textures = json.loads(b64decode(property["value"], validate=True).decode("utf-8"))
            await message.channel.send(embed=embed_skin(textures["textures"]["SKIN"]["url"], textures["profileName"]))


def embed_skin(skin_url, username):
    embed = discord.Embed(
        title = f"{username}'s skin:",
        colour = discord.Colour.gold()
    )
    embed.set_image(url=skin_url)
    return embed
