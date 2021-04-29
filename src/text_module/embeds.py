import discord


async def embed_error_message(embed_description):
    return discord.Embed(
        title = ":exclamation: ERROR.",
        colour = discord.Colour.dark_red(),
        description = f"{embed_description}",
    )


async def embed_sorry_message(embed_description):
    return discord.Embed(
        title = ":exclamation: Sorry, I couldn't complete that.",
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
        colour = discord.Colour(0x3f87a1),
        description = f"{embed_description}",
    )


async def embed_response_without_title(embed_description):
    return discord.Embed(
        colour = discord.Colour(0x3f87a1),
        description = f":information_source: {embed_description}",
    )


async def embed_response_custom_emote(embed_title, embed_description, emote):
    return discord.Embed(
        title = f"{emote} {embed_title}",
        colour = discord.Colour(0x3f87a1),
        description = f"{embed_description}",
    )


async def embed_response_without_title_custom_emote(embed_description, emote):
    return discord.Embed(
        colour = discord.Colour(0x3f87a1),
        description = f"{emote} {embed_description}",
    )


async def embed_failed_counting(embed_title, embed_description):
    return discord.Embed(
        title = f":x: {embed_title}",
        colour = discord.Colour.dark_red(),
        description = f"{embed_description}",
    )


async def embed_youtube_info(metadata):
    youtube_info_embed = discord.Embed(
        title = f"{metadata['title']} - {metadata['uploader']}",
        colour = discord.Color(0xeb4034)
    )

    youtube_info_embed.set_author(icon_url="https://www.iconpacks.net/icons/2/free-youtube-logo-icon-2431-thumb.png", name=" Now playing:")
    youtube_info_embed.set_thumbnail(url=metadata["thumbnail"])
    youtube_info_embed.set_footer(text=f"⠀         👁️ {metadata['view_count']}⠀         |⠀         👍 {metadata['like_count']}⠀         |⠀         👎 {metadata['dislike_count']}⠀         |⠀         ⏱️ {metadata['duration']}s")

    return youtube_info_embed

