import requests
import logging

import data
import verbose.embeds
import cache
from methods import parse_timestamp
from exceptions import StatsNotFoundError
import modules.minecraft.stats.bedwars_stats, \
    modules.minecraft.stats.skywars_stats


hypixel_api_key = data.__secrets["hypixel_api_key"]
if hypixel_api_key == "REPLACE THIS TEXT WITH YOUR HYPIXEL API KEY":
    logging.info("Your hypixel API key had not been set. Get one by going in-game to the hypixel server and typing `/api new`.")

recent_searches = cache.Cache()
hypixel_logo_url = "https://pbs.twimg.com/profile_images/1346968969849171970/DdNypQdN_400x400.png"


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

    if not hypixel_data["success"]:
        await message.channel.send(embed=verbose.embeds.embed_sorry_message("I couldn't fetch data for that player - either you have requested them recently or are spamming the command."))
        return

    # save recent searches to memory so i dont spam the api
    object_to_cache = cache.CachedObject(username, hypixel_data)
    recent_searches.add(object_to_cache)

    first_and_last_login = f"first login: {parse_timestamp(hypixel_data['player']['firstLogin'])}    \
        last login: {parse_timestamp(hypixel_data['player']['lastLogin'])}"

    try:
        player_rank = hypixel_data["player"]["newPackageRank"]
    except KeyError:
        player_rank = "N/A"

    if game == "bw" or game == "bedwars":
        try:
            bedwars_data = hypixel_data["player"]["stats"]["Bedwars"]
            username = f"[{hypixel_data['player']['achievements']['bedwars_level']}☆] {hypixel_data['player']['displayname']}"
            await message.channel.send(embed=modules.minecraft.stats.bedwars_stats.embed_bedwars_stats(username, bedwars_data, hypixel_logo_url, first_and_last_login, player_rank))
        except TypeError:
            await message.channel.send(embed=verbose.embeds.embed_sorry_message("I could not find a user with that name. Please check spelling and try again."))
            return
        except (KeyError, StatsNotFoundError):
            await message.channel.send(embed=verbose.embeds.embed_sorry_message("That user has never played hypixel bedwars."))
            return
    
    elif game == "sw" or game == "skywars":
        try:
            skywars_data = hypixel_data["player"]["stats"]["SkyWars"]
            sw_level = sw_xp_to_level(hypixel_data['player']['stats']['SkyWars']['skywars_experience'])
            username = f"[{sw_level}☆] {hypixel_data['player']['displayname']}"
            await message.channel.send(embed=modules.minecraft.stats.skywars_stats.embed_skywars_stats(username, skywars_data, hypixel_logo_url, first_and_last_login, player_rank))
        except TypeError:
            await message.channel.send(embed=verbose.embeds.embed_sorry_message("I could not find a user with that name. Please check spelling and try again."))
            return
        except (KeyError, StatsNotFoundError):
            await message.channel.send(embed=verbose.embeds.embed_sorry_message("That user has never played hypixel skywars."))
            return


def sw_xp_to_level(xp):
    xp_thresholds = [0, 20, 70, 150, 250, 500, 1000, 2000, 3500, 6000, 10000, 15000]
    if xp >= 15000:
        return int((xp - 15000) / 10000 + 12)
    else:
        for level in range(len(xp_thresholds)):
            if xp < xp_thresholds[level]:
                return level
