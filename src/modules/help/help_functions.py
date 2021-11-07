import verbose.embeds
from modules.help.help_message import HelpMessage
from command_prefix import COMMAND_PREFIX


active_help_messages = []


async def help_message_handler(message):
    try:
        second_parameter = message.content.split(" ")[2]
    except IndexError:
        help_message = HelpMessage(message, default_help_message_content, "Commands")
        await help_message.send()
        return

    if second_parameter == "text":
        help_message = HelpMessage(message, text_help_message_content, "Text Commands")
        await help_message.send()

    elif second_parameter == "image":
        help_message = HelpMessage(message, image_help_message_content, "Image Commands")
        await help_message.send()

    elif second_parameter == "vc":
        help_message = HelpMessage(message, voice_help_message_content, "Voice Commands")
        await help_message.send()
        active_help_messages.append(help_message)

    elif second_parameter == "games":
        help_message = HelpMessage(message, games_help_message_content, "Games Commands")
        await help_message.send()

    elif second_parameter == "flashcards":
        help_message = HelpMessage(message, flashcards_help_message_content, "Flashcard Commands")
        await help_message.send()

    elif second_parameter == "minecraft" or second_parameter == "mc":
        help_message = HelpMessage(message, minecraft_help_message_content, "Minecraft Commands")
        await help_message.send()

    else:
        await message.channel.send(embed=verbose.embeds.embed_warning_message("Must specify valid help message."))
        
    if len(active_help_messages) > 10:
        removed_message = active_help_messages.pop(0)
        await removed_message.clear_reactions()


async def change_help_message_page(bot_message, reaction):
    for saved_message in active_help_messages:
        if saved_message.message == bot_message:
            await saved_message.change_page(reaction)
            break


default_help_message_content = [
    f"• **Text Module**\n    `{COMMAND_PREFIX} help text`\n     _Commands used to add, edit, remove and list keywords._\n",
    f"• **Image Module**\n    `{COMMAND_PREFIX} help image`\n    _Commands used to make images with custom text._\n",
    f"• **Voice Module**\n    `{COMMAND_PREFIX} help vc`\n    _Commands used to playing audio from Youtube or Twitch in a voice channel._\n",
    f"• **Flashcards Module**\n    `{COMMAND_PREFIX} help flashcards`\n    _Commands used to make, use, and edit custom flashcard sets._\n",
    f"• **Games Module**\n    `{COMMAND_PREFIX} help games`\n    _Commands used to play Robo's built-in games._\n",
    f"• **Minecraft Module**\n    `{COMMAND_PREFIX} help mincraft/mc`\n    _Commands used to get info from various minecraft-related APIs._\n",
]

text_help_message_content = [
    f"• `{COMMAND_PREFIX} keyword add [KEYWORD] [VALUE]` \n    _Add a keyword that Robo will check for in your messages. Robo will reply with its value._\n",
    f"• `{COMMAND_PREFIX} keyword remove [KEYWORD]` \n    _Remove a keyword from Robo's list of keywords._\n",
    f"• `{COMMAND_PREFIX} keyword edit [OLD KEYWORD] [RENAMED KEYWORD]` \n    _Edit the name of an existing keyword._\n",
    f"• `{COMMAND_PREFIX} keyword list` \n    _Robo will display a list of all the current keywords and their values on your server._\n",
]

image_help_message_content = [
    f"• `{COMMAND_PREFIX} quote [TYPE] \"[MESSAGE]\" \"[AUTHOR(optional)]\"` \n    _Robo will make a custom image with the image type of your choice, the quote message of your choice and the author of your choice._\n",
]

voice_help_message_content = [
    f"• `{COMMAND_PREFIX} vc join` \n    _Get Robo to join the vc that you are currently in. Any songs in the queue will automatically start playing._\n",
    f"• `{COMMAND_PREFIX} vc leave` \n    _Robo will leave the vc that he is currently in._\n",
    f"• `{COMMAND_PREFIX} vc add [REQUEST(from youtube)]` \n    _Add a youtube video to the queue._\n",
    f"• `{COMMAND_PREFIX} vc skip/next` \n    _Robo will play the next song in the queue._\n",
    f"• `{COMMAND_PREFIX} vc queue [NAME(optional)]` \n    _Shows a list of all songs in the queue specified. If no queue specified, use current queue._\n",
    f"• `{COMMAND_PREFIX} vc save-queue [NAME]` \n    _Saves current queue as a preset with the name [NAME]. Saving another with the same name will overwrite the old one._\n",
    f"• `{COMMAND_PREFIX} vc play-queue [NAME]` \n    _Plays the saved queue with the name [NAME]._\n",
    f"• `{COMMAND_PREFIX} vc queue-list` \n    _Shows a list of all saved queues in your server._\n",
    f"• `{COMMAND_PREFIX} vc loop` \n    _Loops the currently playing song request._\n",
    f"• `{COMMAND_PREFIX} vc queue-loop` \n    _Loops the currently active queue._\n",
    f"• `{COMMAND_PREFIX} vc shuffle` \n    _Shuffles the queue._\n",
    f"• `{COMMAND_PREFIX} vc toggle-np` \n    _Toggles whether you recieve the `Now playing:` message when a new song starts playing._\n",
]

flashcards_help_message_content = [
    f"• `{COMMAND_PREFIX} flashcards new [NAME]` \n    _Robo will guide you through the creation process of a new flashcard set with the name [NAME]._\n",
    f"• `{COMMAND_PREFIX} flashcards end-creation` \n    _Robo will end the flashcard creation process and save your new flashcard set._\n",
    f"• `{COMMAND_PREFIX} flashcards use [NAME]` \n    _Robo will send a message containing the flashcard set [name], which you can navigate using reactions._\n",
    f"• `{COMMAND_PREFIX} flashcards remove [NAME]` \n    _Remove a flashcard set from the list of saved flashcard sets._\n",
    f"• `{COMMAND_PREFIX} flashcards edit [SET] [POSITION] \"[NEW FRONT]\" \"[NEW BACK]\"` \n    _Replace the flashcard in a set with a new card._\n",
    f"• `{COMMAND_PREFIX} flashcards list` \n    _Robo will display a list of all the saved flashcard sets on your server._\n",
]

games_help_message_content = [
    f"• `{COMMAND_PREFIX} games counting [INCREMENT(optional)]` \n    _Start a game of Counting (min 2 people). Count up to the highest number you can, without saying two numbers in a row or sending the wrong number._\n",
]

minecraft_help_message_content = [
    f"• `{COMMAND_PREFIX} minecraft bedwars/bw [USERNAME]` \n    _Robo sends a selection of hypixel bedwars stats for player [USERNAME]._\n",
    f"• `{COMMAND_PREFIX} minecraft skywars/sw [USERNAME]` \n    _Robo sends a selection of hypixel skywars stats for player [USERNAME]._\n",
    f"• `{COMMAND_PREFIX} minecraft skin [USERNAME]` \n    _Robo sends a render of [USERNAME]'s skin._\n",
    f"• `{COMMAND_PREFIX} minecraft skin-texture [USERNAME]` \n    _Robo sends the raw skin texture of player [USERNAME] which can be saved and input to the minecraft launcher for use._\n",
]
