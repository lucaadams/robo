import discord
from exceptions import StatsNotFoundError


def embed_bedwars_stats(username, data, hypixel_logo_url, first_and_last_login, player_rank) -> discord.Embed:
    stats_embed = discord.Embed(
        title = username,
        colour = discord.Colour.gold()
    )

    # get only the data i need from the dict with all the data
    overall_stats_data = get_overall_bedwars_stats(data, player_rank)

    stats_embed.set_author(icon_url=hypixel_logo_url, name=" Overall bedwars stats")
    stats_embed.set_thumbnail(url="https://i.ytimg.com/vi/DQFZ0lJPcs8/maxresdefault.jpg")
    stats_embed.set_footer(text=first_and_last_login)
    
    for stat in overall_stats_data.keys():
        stats_embed.add_field(name=stat, value=f"`{overall_stats_data[stat]}`", inline=True)
    
    return stats_embed


def get_overall_bedwars_stats(data, player_rank) -> discord.Embed:
    try:
        overall_stats_data = {
            "Rank": "[{}]".format(player_rank), "Coins": data["coins"], "Winstreak": data["winstreak"],
            "Wins": data["wins_bedwars"], "Losses": data["losses_bedwars"], "WLR": round(data["wins_bedwars"]/data["losses_bedwars"], 2),
            "Kills": data["kills_bedwars"], "Deaths": data["deaths_bedwars"], "K/D": round(data["kills_bedwars"]/data["deaths_bedwars"], 2),
            "Final Kills": data["final_kills_bedwars"], "Final Deaths": data["final_deaths_bedwars"], "FKDR": round(data["final_kills_bedwars"]/data["final_deaths_bedwars"], 2),
            "Beds Broken": data["beds_broken_bedwars"], "Beds Lost": data["beds_lost_bedwars"], "BBBLR": round(data["beds_broken_bedwars"]/data["beds_lost_bedwars"], 2)
        }
    except:
        raise StatsNotFoundError

    return overall_stats_data

