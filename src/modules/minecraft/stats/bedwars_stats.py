import discord

from exceptions import StatsNotFoundError


hypixel_logo_url = "https://pbs.twimg.com/profile_images/1346968969849171970/DdNypQdN_400x400.png"

corresponding_gamemodes_and_gamecodes = {
    "eight_one": "Solo", "eight_two": "Doubles",
    "four_three": "Threes", "four_four": "Fours"
}


def embed_bedwars_stats(base_player_data, page_number) -> discord.Embed:
    stats_embed = discord.Embed(
        title=base_player_data["username"],
        colour=discord.Colour.gold()
    )

    # get only the data i need from the dict with all the data
    if page_number == 0:
        stats_data, gamemode = get_overall_bedwars_stats(
            base_player_data["user_gamemode-specific_data"], base_player_data["player_rank"])
    else:
        gamecode = page_number_to_gamecode(page_number)
        stats_data, gamemode = get_mode_specific_bedwars_stats(
            base_player_data["user_gamemode-specific_data"], base_player_data["player_rank"], gamecode)

    stats_embed.set_author(icon_url=hypixel_logo_url,
                           name=f" {gamemode} bedwars stats")
    stats_embed.set_thumbnail(url=base_player_data["user_avatar_url"])
    stats_embed.set_footer(text=base_player_data["first_and_last_login"])

    for stat in stats_data.keys():
        stats_embed.add_field(
            name=stat, value=f"`{stats_data[stat]}`", inline=True)

    return stats_embed


def get_overall_bedwars_stats(data, player_rank) -> discord.Embed:
    gamemode = "Overall"
    try:
        overall_stats_data = {
            "Rank": "[{}]".format(player_rank), "Coins": data["coins"], "Winstreak": data["winstreak"],
            "Wins": data["wins_bedwars"], "Losses": data["losses_bedwars"], "WLR": round(data["wins_bedwars"]/data["losses_bedwars"], 2),
            "Kills": data["kills_bedwars"], "Deaths": data["deaths_bedwars"], "K/D": round(data["kills_bedwars"]/data["deaths_bedwars"], 2),
            "Final Kills": data["final_kills_bedwars"], "Final Deaths": data["final_deaths_bedwars"], "FKDR": round(data["final_kills_bedwars"]/data["final_deaths_bedwars"], 2),
            "Beds Broken": data["beds_broken_bedwars"], "Beds Lost": data["beds_lost_bedwars"], "BBBLR": round(data["beds_broken_bedwars"]/data["beds_lost_bedwars"], 2),
            "Games Played": data["games_played_bedwars"], "Diamonds": data["diamond_resources_collected_bedwars"], "Emeralds": data["emerald_resources_collected_bedwars"]
        }
    except:
        raise StatsNotFoundError

    return overall_stats_data, gamemode


def get_mode_specific_bedwars_stats(data, player_rank, gamecode) -> discord.Embed:
    gamemode = corresponding_gamemodes_and_gamecodes[gamecode]

    try:
        overall_stats_data = {
            "Rank": "[{}]".format(player_rank), "Coins": data["coins"], "Winstreak": data[f"{gamecode}_winstreak"],
            "Wins": data[f"{gamecode}_wins_bedwars"], "Losses": data[f"{gamecode}_losses_bedwars"], "WLR": round(data[f"{gamecode}_wins_bedwars"]/data[f"{gamecode}_losses_bedwars"], 2),
            "Kills": data[f"{gamecode}_kills_bedwars"], "Deaths": data["deaths_bedwars"], "K/D": round(data[f"{gamecode}_kills_bedwars"]/data[f"{gamecode}_deaths_bedwars"], 2),
            "Final Kills": data[f"{gamecode}_final_kills_bedwars"], "Final Deaths": data[f"{gamecode}_final_deaths_bedwars"], "FKDR": round(data[f"{gamecode}_final_kills_bedwars"]/data[f"{gamecode}_final_deaths_bedwars"], 2),
            "Beds Broken": data[f"{gamecode}_beds_broken_bedwars"], "Beds Lost": data[f"{gamecode}_beds_lost_bedwars"], "BBBLR": round(data[f"{gamecode}_beds_broken_bedwars"]/data[f"{gamecode}_beds_lost_bedwars"], 2),
            "Games Played": data[f"{gamecode}_games_played_bedwars"], "Diamonds": data[f"{gamecode}_diamond_resources_collected_bedwars"], "Emeralds": data[f"{gamecode}_emerald_resources_collected_bedwars"]
        }
    except:
        raise StatsNotFoundError

    return overall_stats_data, gamemode


def page_number_to_gamecode(page_number):
    corresponding_page_numbers_and_gamecodes = {
        1: "eight_one", 2: "eight_two",
        3: "four_three", 4: "four_four"
    }

    return corresponding_page_numbers_and_gamecodes[page_number]
