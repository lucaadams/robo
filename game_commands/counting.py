import discord

import text_commands.embeds


counting_data = {}


async def start_counting(guild_id, message, increment=1):
    await message.channel.send(embed=await text_commands.embeds.embed_response("Your counting game has started.", f"Type `{increment}` to start"))

    # sets all the required keys in the counting_data dictionary
    counting_data[guild_id] = {}
    counting_data_for_guild = counting_data[guild_id]
    counting_data_for_guild["increment"] = increment
    counting_data_for_guild["messages"] = []
    counting_data_for_guild["counting_has_started"] = True
    counting_data_for_guild["next_number"] = float(increment)


async def check_message(message):
    guild_id = str(message.guild.id)
    if guild_id in counting_data.keys():
        message_float = try_cast_float(message.content)
        if counting_data[guild_id]["counting_has_started"] and message_float != None:
            counting_data[guild_id]["messages"].append(message)
            messages_list_for_guild = counting_data[guild_id]["messages"]

            # checks if youve sent 2 messages in a row
            if len(messages_list_for_guild) > 1 and messages_list_for_guild[len(messages_list_for_guild) - 1].author.id == messages_list_for_guild[len(messages_list_for_guild) - 2].author.id:
                await message.channel.send(embed=await text_commands.embeds.embed_failed_counting("Counting twice in a row is no fun.", f"You counted up to {counting_data[guild_id]['next_number'] - counting_data[guild_id]['increment']}"))
                await message.add_reaction("❌")
                messages_list_for_guild = []
                counting_data[guild_id]["counting_has_started"] = False
                return
            else:
                # checks to see if you typed the right number
                if message_float == counting_data[guild_id]["next_number"]:
                    counting_data[guild_id]["next_number"] += counting_data[guild_id]["increment"]
                    await message.add_reaction("✅")
                else:
                    await message.channel.send(embed=await text_commands.embeds.embed_failed_counting("That's the wrong number.", f"You counted up to {counting_data[guild_id]['next_number'] - counting_data[guild_id]['increment']}"))
                    await message.add_reaction("❌")
                    messages_list_for_guild = []
                    counting_data[guild_id]["counting_has_started"] = False
                    return

        else:
            return


def try_cast_float(message_content):
    try:
        return float(message_content)
    except:
        return None
