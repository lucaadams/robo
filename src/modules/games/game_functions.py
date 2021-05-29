import verbose.embeds
import modules.games.counting


async def start_game(guild_id, message):
    try:
        game = message.content.split(" ")[2]
    except IndexError:
        await message.channel.send(
            embed=verbose.embeds.embed_error_message("Must specify a game.")
        )
        return

    if game == "counting":
        increment = await set_increment(message)
        await modules.games.counting.start_counting(guild_id, message, increment)
    else:
        await message.channel.send(
            embed=verbose.embeds.embed_error_message("That game does not exist.")
        )


async def set_increment(message):
    increment = 1

    try:
        increment = float(message.content.split(" ")[3])
    except ValueError:
        await message.channel.send(
            embed=verbose.embeds.embed_error_message(
                "Increment must be an number. Game will continue with increment `1`."
            )
        )
    except IndexError:
        pass

    return increment
