import requests

import verbose.embeds


SUCCESSFUL_STATUS_CODE = 200

get_uuid_url = "https://api.mojang.com/users/profiles/minecraft/{}"


async def get_uuid(message):
    try:
        username = message.content.split()[3].lower()
    except IndexError:
        await message.channel.send(embed=verbose.embeds.embed_warning_message(f"You must specify a user."))
        return

    uuid_request = requests.get(url=get_uuid_url.format(username))

    if uuid_request.status_code != SUCCESSFUL_STATUS_CODE:
        await message.channel.send(embed=verbose.embeds.embed_sorry_message(f"I could not find a user with the name `{username}`. Please check spelling and try again."))
        return

    uuid = uuid_request.json()["id"]
    username = uuid_request.json()["name"]

    return uuid, username
