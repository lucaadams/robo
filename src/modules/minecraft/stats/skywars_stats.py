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

    overall_stats_data = {
        "Rank": "[{}]".format(player_rank), "Coins": data.get("coins", 0), "Winstreak": data.get("win_streak", 0),
        "Wins": data.get("wins", 0), "Losses": data.get("losses", 0), "WLR": round(data.get("wins", 0)/data.get("losses", 1), 2),
        "Kills": data.get("kills", 0), "Deaths": data.get("deaths", 0), "K/D": round(data.get("kills", 0)/data.get("deaths", 1), 2),
        "Total souls": data.get("souls_gathered", 0), "Heads": data.get("heads", 0), "Chests Opened": data.get("chests_opened", 0),
        "Arrows shot": data.get("arrows_shot", 0), "Arrows Hit": data.get("arrows_hit", 0), "Accuracy": f"{round((data.get('arrows_hit', 0)/data.get('arrows_shot', 1)) * 100, 2)}%"
    }

    return overall_stats_data, gamemode


def get_mode_specific_skywars_stats(data, player_rank, gamecode) -> discord.Embed:
    gamemode = corresponding_gamemodes_and_gamecodes[gamecode]

    overall_stats_data = {
        "Rank": "[{}]".format(player_rank), "Coins": data.get("coins", 0), "Winstreak": data.get("win_streak", 0),
        "Wins": data.get(f"wins_{gamecode}", 0), "Losses": data.get(f"losses_{gamecode}", 0), "WLR": round(data.get(f"wins_{gamecode}", 0)/data.get(f"losses_{gamecode}", 1), 2),
        "Kills": data.get(f"kills_{gamecode}", 0), "Deaths": data.get(f"deaths_{gamecode}", 0), "K/D": round(data.get(f"kills_{gamecode}", 0)/data.get(f"deaths_{gamecode}", 1), 2)
    }

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
