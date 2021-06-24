import verbose.embeds


counting_data = {}


async def start_counting(guild_id, message, increment=1):
    await message.channel.send(embed=verbose.embeds.embed_response("Your counting game has started.", f"Type `{increment}` to start"))
    counting_data[guild_id] = {
        "increment": increment,
        "messages": [],
        "counting_has_started": True,
        "next_number": float(increment)
    }


async def check_message(message):
    guild_id = str(message.guild.id)
    if guild_id in counting_data.keys():
        message_float = try_cast_float(message.content)
        if counting_data[guild_id]["counting_has_started"] and message_float is not None:
            counting_data[guild_id]["messages"].append(message)

            person_sent_two_messages_in_a_row = await check_if_person_sent_two_messages_in_a_row(
                message, counting_data[guild_id]["messages"])
            if person_sent_two_messages_in_a_row:
                return

            await check_for_incorrect_number(message, message_float)


async def check_if_person_sent_two_messages_in_a_row(message, messages_list_for_guild):
    guild_id = str(message.guild.id)
    if len(messages_list_for_guild) > 1 and messages_list_for_guild[len(messages_list_for_guild) - 1].author.id == \
            messages_list_for_guild[len(messages_list_for_guild) - 2].author.id:
        await message.add_reaction("❌")
        await message.channel.send(embed=verbose.embeds.embed_failed_counting(
            "Counting twice in a row is no fun.", f"You counted up to {counting_data[guild_id]['next_number'] - counting_data[guild_id]['increment']}"))
        await send_stats(message, messages_list_for_guild)
        messages_list_for_guild = []
        counting_data[guild_id]["counting_has_started"] = False
        return True
    return False


async def check_for_incorrect_number(message, message_float):
    guild_id = str(message.guild.id)
    if message_float == counting_data[guild_id]["next_number"]:
        counting_data[guild_id]["next_number"] += counting_data[guild_id]["increment"]
        await message.add_reaction("✅")
    else:
        await message.add_reaction("❌")
        await message.channel.send(embed=verbose.embeds.embed_failed_counting(
            "That's the wrong number.", f"You counted up to {counting_data[guild_id]['next_number'] - counting_data[guild_id]['increment']}"))
        await send_stats(message, counting_data[guild_id]["messages"])
        counting_data[guild_id]["messages"] = []
        counting_data[guild_id]["counting_has_started"] = False


def try_cast_float(message_content):
    try:
        return float(message_content)
    except ValueError:
        return None


async def send_stats(message, messages_list_for_guild):
    final_stats = {}
    total_messages = 0
    for msg in messages_list_for_guild:
        user = msg.author.mention
        if user not in final_stats.keys():
            final_stats[user] = 1
            total_messages += 1
        else:
            final_stats[user] += 1
            total_messages += 1

    stats_message = ""
    for user in final_stats.keys():
        stats_message += f"{user} - {final_stats[user]} messages, {int((final_stats[user] / total_messages) * 100)}% helpful.\n"
    await message.channel.send(embed=verbose.embeds.embed_response("Counting Stats:", stats_message))
