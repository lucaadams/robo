from discord import user
import requests
import logging
import discord

import bot
import data
import verbose.embeds
import cache
from methods import parse_timestamp
from exceptions import StatsNotFoundError
import modules.minecraft.stats.bedwars_stats, \
    modules.minecraft.stats.skywars_stats
from modules.minecraft.user_skins.get_user_skin import get_user_avatar


hypixel_api_key = data.__secrets["hypixel_api_key"]
if hypixel_api_key == "REPLACE THIS TEXT WITH YOUR HYPIXEL API KEY":
    logging.info("Your hypixel API key had not been set. Get one by going in-game to the hypixel server and typing `/api new`.")

recent_searches = cache.Cache()
sent_stats_messages = []

emoji_list = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣"]
stop_emoji = "⏹️"


class StatsMessage:
    def __init__(self, message, base_player_data: dict, gamemode: str):
        self.message = message
        self.base_player_data = base_player_data
        self.gamemode = gamemode


async def hypixel_command_handler(message):
    try:
        game = message.content.split()[2].lower()
        username = message.content.split()[3].lower()
    except IndexError:
        await message.channel.send(embed=verbose.embeds.embed_error_message(f"You must include both parameters `[GAME]` and `[USERNAME]`."))
        return

    # try to get search from cache. if it didn't work, send req
    hypixel_data = recent_searches.get_object(username)
    if hypixel_data is None:
        async with message.channel.typing():
            # send request for hypixel data from a specific user
            hypixel_data = requests.get(
                url = "https://api.hypixel.net/player",
                params = {
                    "key": hypixel_api_key,
                    "name": username
                }
            ).json()

        # check if unsuccessful request
        if not hypixel_data["success"]:
            await message.channel.send(embed=verbose.embeds.embed_sorry_message("I couldn't fetch data for that player - either you have requested them recently or are spamming the command."))
            return

        # check if player exists
        if hypixel_data["player"] is None:
            await message.channel.send(embed=verbose.embeds.embed_sorry_message("That player does not exist. Please check spelling and try again."))
            return

        # save recent searches to memory so i dont spam the api
        object_to_cache = cache.CachedObject(username, hypixel_data)
        recent_searches.add(object_to_cache)

    user_avatar_url = await get_user_avatar(message)

    first_and_last_login = f"first login: {parse_timestamp(hypixel_data['player']['firstLogin'])}    \
        last login: {parse_timestamp(hypixel_data['player']['lastLogin'])}"

    try:
        player_rank = hypixel_data["player"]["newPackageRank"]
        if player_rank == "MVP_PLUS":
            player_rank = "MVP+"
    except KeyError:
        player_rank = "N/A"

    if game == "bw" or game == "bedwars":
        try:
            username = f"[{hypixel_data['player']['achievements']['bedwars_level']}☆] {hypixel_data['player']['displayname']}"
            base_player_data = {
                "username": username, "gamemode": "bw", "user_gamemode-specific_data": hypixel_data["player"]["stats"]["Bedwars"], 
                "first_and_last_login": first_and_last_login, "player_rank": player_rank, "user_avatar_url": user_avatar_url
            }
            bw_stats_message = await message.channel.send(embed=modules.minecraft.stats.bedwars_stats.embed_bedwars_stats(base_player_data, 0))
            sent_message = StatsMessage(bw_stats_message, base_player_data, "bw")
            sent_stats_messages.append(sent_message)
            await add_reaction(bw_stats_message)
        except TypeError:
            await message.channel.send(embed=verbose.embeds.embed_sorry_message("I could not find a user with that name. Please check spelling and try again."))
            return
        except (KeyError, StatsNotFoundError):
            await message.channel.send(embed=verbose.embeds.embed_sorry_message("That user has never played hypixel bedwars."))
            return
    
    elif game == "sw" or game == "skywars":
        try:
            skywars_data = hypixel_data["player"]["stats"]["SkyWars"]
            username = f"[{skywars_data['levelFormatted'][-3:].strip('§f')}] {hypixel_data['player']['displayname']}"
            base_player_data = {
                "username": username, "gamemode": "sw", "user_gamemode-specific_data": skywars_data, 
                "first_and_last_login": first_and_last_login, "player_rank": player_rank, "user_avatar_url": user_avatar_url
            }
            sw_stats_message = await message.channel.send(embed=modules.minecraft.stats.skywars_stats.embed_skywars_stats(base_player_data))
            sent_message = StatsMessage(sw_stats_message, hypixel_data, "sw")
            sent_stats_messages.append(sent_message)
            await add_reaction(sw_stats_message)
        except TypeError:
            await message.channel.send(embed=verbose.embeds.embed_sorry_message("I could not find a user with that name. Please check spelling and try again."))
            return
        except (KeyError, StatsNotFoundError):
            await message.channel.send(embed=verbose.embeds.embed_sorry_message("That user has never played hypixel skywars."))
            return


async def add_reaction(bot_message):
    for emoji in emoji_list:
        await bot_message.add_reaction(emoji)
    await bot_message.add_reaction(stop_emoji)


async def change_page(bot_message, reaction):
    # first, get the stats of the user that the sent message was about
    message_index_in_sent_messages = None
    for index, stats_message in enumerate(sent_stats_messages):
        if bot_message == stats_message.message:
            message_index_in_sent_messages = index
    
    if message_index_in_sent_messages is None:
        return

    if reaction.emoji == stop_emoji:
        # remove all reactions
        await sent_stats_messages[message_index_in_sent_messages].message.clear_reactions()
        sent_stats_messages.pop(message_index_in_sent_messages)
        return

    # get required page number
    page_number = -1
    for index in range(len(emoji_list)):
        if reaction.emoji == emoji_list[index]:
            page_number = index
            break

    if page_number == -1:
        return

    if sent_stats_messages[message_index_in_sent_messages].gamemode == "bw":
        await bot_message.edit(embed=modules.minecraft.stats.bedwars_stats.embed_bedwars_stats(
            sent_stats_messages[message_index_in_sent_messages].base_player_data, page_number))


def sw_xp_to_level(xp):
    xp_thresholds = [0, 20, 70, 150, 250, 500, 1000, 2000, 3500, 6000, 10000, 15000]
    if xp >= 15000:
        return int((xp - 15000) / 10000 + 12)
    else:
        for level, threshold in enumerate(xp_thresholds):
            if xp < threshold:
                return level
