import minecraft_module.hypixel


async def minecraft_command_handler(message):
    second_parameter = message.content.split()[2]

    if second_parameter == "bw" or second_parameter == "sw":
        await minecraft_module.hypixel.hypixel_command_handler(message)
