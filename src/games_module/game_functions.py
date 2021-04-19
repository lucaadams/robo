import discord

import text_module.embeds
import games_module.counting


async def start_game(guild_id, message):
    try:
        game = message.content.split(" ")[2]
    except:
        await message.channel.send(embed=await text_module.embeds.embed_error_message("Must specify a game."))
        return

    increment = 1
    try:
        increment = float(message.content.split(" ")[3])
    except ValueError:
        await message.channel.send(embed=await text_module.embeds.embed_error_message("Increment must be an number. Game will continue with increment `1`."))
    except IndexError:
        pass

    if game == "counting":
        await games_module.counting.start_counting(guild_id, message, increment)
    else:
        await message.channel.send(embed=await text_module.embeds.embed_error_message("That game does not exist."))
