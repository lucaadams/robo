import discord

from data import data
import verbose.embeds


DEFAULT_GUILD_FLASHCARD_DATA = {
    "flashcard_creation_in_progress": False,
    "channel": None,
    "user": None,
    "current_flashcard_set_name": None,
    "current_flashcard_set": {}
}

DEFAULT_GUILD_ACTIVE_FLASHCARD_SETS_DATA = {
    "name_of_set": None,
    "active_set": None,
    "message": None,
    "index": 0,
    "current_side": "front"
}

flashcard_data = {}
active_flashcard_sets = {}
emoji_list = ["⏪", "🔁", "⏩"]


async def flashcard_command_handler(message):
    guild_id = str(message.guild.id)
    second_parameter = message.content.split()[2]

    if guild_id not in flashcard_data:
        flashcard_data[guild_id] = DEFAULT_GUILD_FLASHCARD_DATA.copy()

    if guild_id not in active_flashcard_sets:
        active_flashcard_sets[guild_id] = DEFAULT_GUILD_ACTIVE_FLASHCARD_SETS_DATA.copy()

    if second_parameter == "new":
        if flashcard_data[guild_id]["flashcard_creation_in_progress"]:
            await message.channel.send(embed=verbose.embeds.embed_sorry_message("Only one flashcard set can be created at a time."))
            return
        
        await create_new_flashcards_set(message)

    elif second_parameter == "end-creation" or second_parameter == "stop-creation":
        await end_flashcard_creation(message)

    elif second_parameter == "use":
        await setup_flashcard_use(message)

    elif second_parameter == "edit":
        await edit_flashcard_set(message)

    elif second_parameter == "list":
        await send_flashcard_set_list(message)

    else:
        await message.channel.send(embed=verbose.embeds.embed_error_message("That command does not exist."))


async def create_new_flashcards_set(message):
    try:
        flashcard_set_name = message.content.split()[3]
    except IndexError:
        await message.channel.send(embed=verbose.embeds.embed_error_message("You must specify a name for your flashcard set."))
        return

    guild_id = str(message.guild.id)

    flashcard_data[guild_id] = {
        "flashcard_creation_in_progress": True,
        "user": message.author,
        "channel": message.channel,
        "current_flashcard_set_name": flashcard_set_name,
        "current_flashcard_set": {}
    }

    await message.channel.send(embed=verbose.embeds.embed_response(
        "Flashcard creation begun.",
        f"Every message that {flashcard_data[guild_id]['user'].mention} sends in the format \n`\"[FLASHCARD front]\" \"[FLASHCARD DEFINITION]\"` \n\
            will be added to the flashcard set with the name `{flashcard_data[guild_id]['current_flashcard_set_name']}`. \nBound to {flashcard_data[guild_id]['channel'].mention}")
    )


async def add_flashcard_to_set(message):
    guild_id = str(message.guild.id)
    flashcard_front = message.content.split('"')[1]
    flashcard_definition = message.content.split('"')[3]

    flashcard_data[guild_id]["current_flashcard_set"][flashcard_front] = flashcard_definition


async def end_flashcard_creation(message):
    guild_id = str(message.guild.id)

    if not flashcard_data[guild_id]["flashcard_creation_in_progress"]:
        await message.channel.send(embed=verbose.embeds.embed_error_message("You cannot end creation if no creation has started."))

    if message.author != flashcard_data[guild_id]["user"]:
        await message.channel.send(embed=verbose.embeds.embed_sorry_message("Only the flashcard set creator can end creation."))
        return

    flashcard_set_name = flashcard_data[guild_id]["current_flashcard_set_name"]
    guild_data = data.get_guild_data(guild_id)
    guild_data["flashcard_sets"][flashcard_set_name] = flashcard_data[guild_id]["current_flashcard_set"].copy()
    data.set_guild_data(guild_id, guild_data)

    await message.channel.send(embed=verbose.embeds.embed_successful_action(f"Your flashcard set `{flashcard_set_name}` has been saved."))

    # reset guild flashcard data 
    flashcard_data[guild_id] = DEFAULT_GUILD_FLASHCARD_DATA.copy()


async def setup_flashcard_use(message):
    guild_id = str(message.guild.id)

    try:
        flashcard_set_to_use = message.content.split()[3]
    except IndexError:
        await message.channel.send(embed=verbose.embeds.embed_error_message("You must specify a flashcard set to use."))
        return

    flashcard_sets = data.get_guild_data(guild_id)["flashcard_sets"]

    if flashcard_set_to_use not in flashcard_sets.keys():
        await message.channel.send(embed=verbose.embeds.embed_sorry_message("That flashcard set does not exist. Please check spelling and try again."))
        return

    if flashcard_data[guild_id]["flashcard_creation_in_progress"]:
        await active_flashcard_sets[guild_id]["message"].clear_reactions()

    active_flashcard_sets[guild_id] = {
        "name_of_set": flashcard_set_to_use,
        "active_set": flashcard_sets[flashcard_set_to_use],
        "message": await message.channel.send(embed=flashcard_embed(flashcard_set_to_use, flashcard_sets[flashcard_set_to_use], 0, "front")),
        "index": 0,
        "current_side": "front"
    }

    for emoji in emoji_list:
        await active_flashcard_sets[guild_id]["message"].add_reaction(emoji)


async def use_flashcards(bot_message, reaction):
    guild_id = str(bot_message.guild.id)
    if guild_id in active_flashcard_sets and bot_message.id != active_flashcard_sets[guild_id]["message"].id:
        return

    try:
        flashcard_set_for_guild = active_flashcard_sets[guild_id]
    except:
        return

    if reaction.emoji == emoji_list[1]:
        if flashcard_set_for_guild["current_side"] == "front":
            flashcard_set_for_guild["current_side"] = "back"
        elif flashcard_set_for_guild["current_side"] == "back":
            flashcard_set_for_guild["current_side"] = "front"
        else:
            raise ValueError("Current side is not front or back... somehow.")

    if reaction.emoji == emoji_list[2]:
        flashcard_set_for_guild["index"] += 1 if flashcard_set_for_guild["index"] < (len(flashcard_set_for_guild["active_set"]) - 1) else 0
        flashcard_set_for_guild["current_side"] = "front"

    if reaction.emoji == emoji_list[0]:
        flashcard_set_for_guild["index"] -= 1 if flashcard_set_for_guild["index"] > 0 else 0
        flashcard_set_for_guild["current_side"] = "front"

    await bot_message.edit(embed=flashcard_embed(
        flashcard_set_for_guild["name_of_set"],
        flashcard_set_for_guild["active_set"],
        flashcard_set_for_guild["index"],
        flashcard_set_for_guild["current_side"]
    ))


async def send_flashcard_set_list(message):
    guild_id = str(message.guild.id)

    flashcard_sets = data.get_guild_data(guild_id)["flashcard_sets"]
    total_desc = ""
    for flashcard_set in flashcard_sets:
        total_desc += f"`{flashcard_set}` - {len(flashcard_sets[flashcard_set])} terms\n"
    if total_desc == "":
        await message.channel.send(embed=verbose.embeds.embed_response_without_title("You do not have any saved flashcard sets."))
        return
    
    await message.channel.send(embed=verbose.embeds.embed_response("Saved flashcard sets:", total_desc))


def flashcard_embed(name_of_set, flashcard_set, index, side):
    flashcard_set_keys = list(flashcard_set)
    if side == "front":
        content = flashcard_set_keys[index]
    elif side == "back":
        content = flashcard_set[flashcard_set_keys[index]]
    else:
        raise ValueError("A side which is not \"front\" or \"back\" was passed in.")

    embed = discord.Embed(
        title = name_of_set,
        colour = discord.Colour(0x67858a),
        description = content,
    )
    embed.set_footer(text=f"{index + 1} / {len(flashcard_set)} - {side}side")

    return embed
