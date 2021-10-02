import requests
from base64 import b64decode
import json
import logging

import verbose.embeds
import cache
from modules.minecraft.get_uuid import get_uuid
from modules.minecraft.user_skins.skin_embeds import embed_skin


SUCCESSFUL_STATUS_CODE = 200

get_uuid_url = "https://api.mojang.com/users/profiles/minecraft/{username}"
get_user_info_url = "https://sessionserver.mojang.com/session/minecraft/profile/{uuid}"

recent_searches = cache.Cache()


async def get_user_skin_texture(message):
    try:
        username = message.content.split()[3].lower()
    except IndexError:
        await message.channel.send(embed=verbose.embeds.embed_warning_message(f"You must specify a user."))
        return

    # only send request if user info is not in cache
    if username in recent_searches.object_keys():
        user_info = recent_searches.get_object(username=username)
    else:
        # first send request for the UUID of USER, then send request using that UUID to get more data including skin url
        with message.channel.typing():
            try:
                uuid, username = await get_uuid(message)
            except TypeError:
                return

            user_info_request = requests.get(
                url=get_user_info_url.format(uuid=uuid))

        logging.info("Request successfully sent to mojang api")

        user_info = user_info_request.json()
        object_to_cache = cache.CachedObject(username, user_info)
        recent_searches.add(object_to_cache)

    # search properties for the "textures" property where i can get the user's skin
    for property_ in user_info["properties"]:
        if property_["name"] == "textures":
            # decode skin code from Base64 to return a json file with user textures
            # `property_["value"]` is the value of the textures property
            textures = json.loads(
                b64decode(property_["value"], validate=True).decode("utf-8"))
            await message.channel.send(embed=embed_skin(textures["textures"]["SKIN"]["url"], textures["profileName"]))
