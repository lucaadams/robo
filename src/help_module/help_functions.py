import text_module.embeds


async def help_message_handler(message, COMMAND_PREFIX):
    try:
        second_parameter = message.content.split(" ")[2]
    except IndexError:
        await default_help_message(message, COMMAND_PREFIX)
        return
    except:
        await message.channel.send(embed=text_module.embeds.embed_error_message("Something went wrong whilst trying to execute that command."))

    if second_parameter == "text":
        await text_help_message(message, COMMAND_PREFIX)

    elif second_parameter == "image":
        await image_help_message(message, COMMAND_PREFIX)

    elif second_parameter == "voice":
        await voice_help_message(message, COMMAND_PREFIX)

    elif second_parameter == "games":
        await games_help_message(message, COMMAND_PREFIX)

    else:
        await message.channel.send(embed=text_module.embeds.embed_error_message("Must specify valid help message."))

async def default_help_message(message, COMMAND_PREFIX):
    await message.channel.send(embed=text_module.embeds.embed_response_custom_emote("Commands:", f'''
    • **Text Module**\n    `{COMMAND_PREFIX} help text`\n     _Commands used to add, edit, remove and list keywords._\n
    • **Image Module**\n    `{COMMAND_PREFIX} help image`\n    _Commands used to make images with custom text._\n
    • **Voice Module**\n    `{COMMAND_PREFIX} help voice`\n    _Commands used to playing audio from Youtube or Twitch in a voice channel._\n
    • **Games Module**\n    `{COMMAND_PREFIX} help games`\n    _Commands used to play Robo's built-in games._\n
    ''', ":page_with_curl:"))


async def text_help_message(message, COMMAND_PREFIX):
    await message.channel.send(embed=text_module.embeds.embed_response_custom_emote("Text Commands:", f'''
    • `{COMMAND_PREFIX} add [keyword] [value]` \n    _Add a keyword that Robo will check for in your messages. Robo will reply with its value._\n
    • `{COMMAND_PREFIX} remove [keyword]` \n    _Remove a keyword from Robo's list of keywords._\n
    • `{COMMAND_PREFIX} edit [old keyword] [renamed keyword]` \n    _Edit the name of an existing keyword._\n
    • `{COMMAND_PREFIX} list` \n    _Robo will display a list of all the current keywords and their values on your server._\n
    ''', ":page_with_curl:"))


async def image_help_message(message, COMMAND_PREFIX):
    await message.channel.send(embed=text_module.embeds.embed_response_custom_emote("Image Commands:", f'''
    • `{COMMAND_PREFIX} quote [image type] "[quote message]" "[OPTIONAL: quote author]"` \n    _Robo will make a custom image with the image type of your choice, the quote message of your choice and the author of your choice._\n
    ''', ":page_with_curl:"))


async def voice_help_message(message, COMMAND_PREFIX):
    await message.channel.send(embed=text_module.embeds.embed_response_custom_emote("Voice Commands:", f'''
    • `{COMMAND_PREFIX} vc join` \n    _Get Robo to join the vc that you are currently in. Any songs in the queue will automatically start playing._\n
    • `{COMMAND_PREFIX} vc leave` \n    _Robo will leave the vc that he is currently in._\n
    • `{COMMAND_PREFIX} vc add [request (youtube)]` \n    _Add a youtube video to the queue._\n
    • `{COMMAND_PREFIX} vc skip` \n    _Robo will play the next song in the queue._\n
    • `{COMMAND_PREFIX} vc loop` \n    _Loops the currently playing song request._\n
    • `{COMMAND_PREFIX} vc queue` \n    _Shows a list of all song requests in the queue._\n
    ''', ":page_with_curl:"))


async def games_help_message(message, COMMAND_PREFIX):
    await message.channel.send(embed=text_module.embeds.embed_response_custom_emote("Text Commands:", f'''
    • `{COMMAND_PREFIX} games counting [OPTIONAL: increment]` \n    _Start a game of Counting (min 2 people). Count up to the highest number you can, without saying two numbers in a row or sending the wrong number._\n
    ''', ":page_with_curl:"))
