import verbose.embeds
import modules.minecraft.hypixel
import modules.minecraft.get_user_skin_texture


async def minecraft_command_handler(message):
    second_parameter = message.content.split()[2]

    if second_parameter == "bw" or second_parameter == "sw":
        await modules.minecraft.hypixel.hypixel_command_handler(message)

    elif second_parameter == "skin":
        await modules.minecraft.get_user_skin_texture.get_user_skin_texture(message)

    else:
        await message.channel.send(embed=verbose.embeds.embed_error_message("That command does not exist."))
