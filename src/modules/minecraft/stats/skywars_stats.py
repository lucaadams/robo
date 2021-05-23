import discord
from exceptions import StatsNotFoundError


hypixel_logo_url = "https://pbs.twimg.com/profile_images/1346968969849171970/DdNypQdN_400x400.png"

corresponding_gamemodes_and_gamecodes = {
    "solo_normal": "Solo normal", "team_normal": "Teams normal",
    "solo_insane": "Solo insane", "team_insane": "Teams insane"
}


def embed_skywars_stats(base_player_data, page_number) -> discord.Embed:
    stats_embed = discord.Embed(
        title=base_player_data["username"],
        colour=discord.Colour.gold()
    )

    if page_number == 0:
        overall_stats_data, gamemode = get_overall_skywars_stats(
            base_player_data["gamemode_specific_data"], base_player_data["player_rank"])
    else:
        gamecode = page_number_to_gamecode(page_number)
        overall_stats_data, gamemode = get_mode_specific_skywars_stats(
            base_player_data["gamemode_specific_data"], base_player_data["player_rank"], gamecode)

    stats_embed.set_author(icon_url=hypixel_logo_url,
                           name=f" {gamemode} skywars stats")
    stats_embed.set_thumbnail(url=base_player_data["user_avatar_url"])
    stats_embed.set_footer(text=base_player_data["first_and_last_login"])

    for stat in overall_stats_data.keys():
        stats_embed.add_field(
            name=stat, value=f"`{overall_stats_data[stat]}`", inline=True)

    return stats_embed


def get_overall_skywars_stats(data, player_rank) -> discord.Embed:
    gamemode = "Overall"

    try:
        overall_stats_data = {
            "Rank": "[{}]".format(player_rank), "Coins": data["coins"], "Winstreak": data["win_streak"],
            "Wins": data["wins"], "Losses": data["losses"], "WLR": round(data["wins"]/data["losses"], 2),
            "Kills": data["kills"], "Deaths": data["deaths"], "K/D": round(data["kills"]/data["deaths"], 2),
            "Total souls": data["souls_gathered"], "Heads": data["heads"], "Chests Opened": data["chests_opened"],
            "Arrows shot": data["arrows_shot"], "Arrows Hit": data["arrows_hit"], "Accuracy": f"{round((data['arrows_hit']/data['arrows_shot']) * 100, 2)}%"
        }
    except:
        raise StatsNotFoundError

    return overall_stats_data, gamemode


def get_mode_specific_skywars_stats(data, player_rank, gamecode) -> discord.Embed:
    gamemode = corresponding_gamemodes_and_gamecodes[gamecode]

    try:
        overall_stats_data = {
            "Rank": "[{}]".format(player_rank), "Coins": data["coins"], "Winstreak": data["win_streak"],
            "Wins": data[f"wins_{gamecode}"], "Losses": data[f"losses_{gamecode}"], "WLR": round(data[f"wins_{gamecode}"]/data[f"losses_{gamecode}"], 2),
            "Kills": data[f"kills_{gamecode}"], "Deaths": data[f"deaths_{gamecode}"], "K/D": round(data[f"kills_{gamecode}"]/data[f"deaths_{gamecode}"], 2),

        }
    except:
        raise StatsNotFoundError

    return overall_stats_data, gamemode


def page_number_to_gamecode(page_number):
    corresponding_page_numbers_and_gamecodes = {
        1: "solo_normal", 2: "teams_normal",
        3: "solo_insane", 4: "teams_insane"
    }

    return corresponding_page_numbers_and_gamecodes[page_number]


def page_number_to_gamecode(page_number):
    corresponding_page_numbers_and_gamecodes = {
        1: "solo_normal", 2: "team_normal",
        3: "solo_insane", 4: "team_insane"
    }

    return corresponding_page_numbers_and_gamecodes[page_number]
