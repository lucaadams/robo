import discord


def embed_skin(skin_texture_url, username):
    embed = discord.Embed(
        title=f"{username}'s skin:",
        colour=discord.Colour.gold()
    )
    embed.set_image(url=skin_texture_url)
    return embed
