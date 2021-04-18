import discord


async def embed_error_message(embed_description):
    return discord.Embed(
        title = ":exclamation: ERROR:",
        colour = discord.Colour.dark_red(),
        description = f"{embed_description}",
    )


async def embed_successful_action(embed_description):
    return discord.Embed(
        title = ":white_check_mark: Success!",
        colour = discord.Colour.green(),
        description = f"{embed_description}",
    )


async def embed_response(embed_title, embed_description):
    return discord.Embed(
        title = f":information_source: {embed_title}",
        colour = discord.Colour(0x9dacc4),
        description = f"{embed_description}",
    )


async def embed_failed_counting(embed_title, embed_description):
    return discord.Embed(
        title = f":x: {embed_title}",
        colour = discord.Colour.dark_red(),
        description = f"{embed_description}",
    )
