import discord


def embed_error_message(embed_description):
    return discord.Embed(
        title = ":exclamation: ERROR",
        colour = discord.Colour.dark_red(),
        description = f"{embed_description}",
    )


def embed_warning_message(embed_description):
    return discord.Embed(
        colour = discord.Colour(0xfcbb38),
        description = f":warning: {embed_description}",
    )


def embed_sorry_message(embed_description):
    return discord.Embed(
        title = ":exclamation: Sorry, I couldn't complete that.",
        colour = discord.Colour.dark_red(),
        description = f"{embed_description}",
    )


def embed_successful_action(embed_description):
    return discord.Embed(
        title = ":white_check_mark: Success!",
        colour = discord.Colour.green(),
        description = f"{embed_description}",
    )


def embed_response(embed_title, embed_description):
    return discord.Embed(
        title = f":information_source: {embed_title}",
        colour = discord.Colour(0x3f87a1),
        description = f"{embed_description}",
    )


def embed_response_without_title(embed_description):
    return discord.Embed(
        colour = discord.Colour(0x3f87a1),
        description = f":information_source: {embed_description}",
    )


def embed_response_custom_emote(embed_title, embed_description, emote):
    return discord.Embed(
        title = f"{emote} {embed_title}",
        colour = discord.Colour(0x3f87a1),
        description = f"{embed_description}",
    )


def embed_response_without_title_custom_emote(embed_description, emote):
    return discord.Embed(
        colour = discord.Colour(0x3f87a1),
        description = f"{emote} {embed_description}",
    )


def embed_failed_counting(embed_title, embed_description):
    return discord.Embed(
        title = f":x: {embed_title}",
        colour = discord.Colour.dark_red(),
        description = f"{embed_description}",
    )
