import discord
from exceptions import StatsNotFoundError


def embed_skywars_stats(username, data, hypixel_logo_url, first_and_last_login, player_rank) -> discord.Embed:
    stats_embed = discord.Embed(
        title = username,
        colour = discord.Colour.gold()
    )

    overall_stats_data = get_overall_skywars_stats(data, player_rank)

    stats_embed.set_author(icon_url=hypixel_logo_url, name=" Overall skywars stats")
    stats_embed.set_thumbnail(url="https://static.wikia.nocookie.net/mineplex/images/b/b6/Skywarslogo.png/revision/latest?cb=20190727041147")
    stats_embed.set_footer(text=first_and_last_login)
    
    for stat in overall_stats_data.keys():
        stats_embed.add_field(name=stat, value=f"`{overall_stats_data[stat]}`", inline=True)
    
    return stats_embed


def get_overall_skywars_stats(data, player_rank) -> discord.Embed:
    try:
        overall_stats_data = {
            "Rank": "[{}]".format(player_rank), "Coins": data["coins"], "Winstreak": data["win_streak"],
            "Wins": data["wins"], "Losses": data["losses"], "WLR": round(data["wins"]/data["losses"], 2),
            "Kills": data["kills"], "Deaths": data["deaths"], "K/D": round(data["kills"]/data["deaths"], 2),
            "Souls": data["souls"], "Heads": data["heads"], "Chests Opened": data["chests_opened"],
            "Arrows shot": data["arrows_shot"], "Arrows Hit": data["arrows_hit"], "Accuracy": f"{round((data['arrows_hit']/data['arrows_shot']) * 100, 2)}%"
        }
    except:
        raise StatsNotFoundError

    return overall_stats_data
