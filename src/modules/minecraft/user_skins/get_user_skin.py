from modules.minecraft.get_uuid import get_uuid
from modules.minecraft.user_skins.skin_embeds import embed_skin


SUCCESSFUL_STATUS_CODE = 200

get_skin_render_url = "https://crafatar.com/renders/body/{uuid}?overlay&default=MHF_Steve"
get_avatar_url = "https://crafatar.com/avatars/{uuid}?overlay&default=MHF_Steve"


async def send_user_skin_render(message):
    try:
        uuid, username = await get_uuid(message)
    except TypeError:
        return

    skin_render_url = get_skin_render_url.format(uuid=uuid)

    await message.channel.send(embed=embed_skin(skin_render_url, username))


async def get_user_avatar(message):
    try:
        uuid, _ = await get_uuid(message)
    except TypeError:
        return
        
    url = get_avatar_url.format(uuid=uuid)
    return url
