import discord
import random
import os
import io
import textwrap
from PIL import Image, ImageDraw, ImageFont

import text_commands.embeds


async def execute_quote_command(message):
    image_type = message.content.split(" ")[2]

    if image_type == "colour":
        await colour_quote_generator(message)

    elif image_type == "grey":
        await grey_quote_generator(message)

    else:
        await message.channel.send(embed=await text_commands.embeds.embed_error_message("You must specify a valid image type ('grey' or 'colour')"))


async def colour_quote_generator(message):
    image_options = ["flowerfield1.png", "flowerfield2.png", "flowerfield3.png", "rainbow.png", "sky.png"]
    image = Image.open(f"image_commands/quote_images/colourful/{image_options[random.randint(0, 4)]}")
    font = ImageFont.truetype("image_commands/quote_images/fonts/Kiss_Boom.ttf", 130)

    try:
        quote_message = message.content.split('"')[1]
    except:
        await message.channel.send(embed=await text_commands.embeds.embed_error_message("Must specify a quote author."))

    quote_message = quote_message.strip(" ")
    quote_message_split = quote_message.split(" ")
    chars_on_this_line = 0
    max_chars_per_line = 30
    quote_message_wrap = ""
    for word in quote_message_split:
        quote_message_wrap += word + " "
        chars_on_this_line += len(word)
        if chars_on_this_line >= max_chars_per_line:
            quote_message_wrap = quote_message_wrap + "\n"
            chars_on_this_line = 0

    quote_person = message.content.split('"')[3]
    quote = f'"{quote_message_wrap}" \n         -{quote_person}'

    image_with_message = ImageDraw.Draw(image)
    image_with_message.text((300, 200), quote, (0, 0, 0), font=font)

    image.save("image_commands/quote_images/temp/temp_image.png")
    await message.channel.send(file=discord.File("image_commands/quote_images/temp/temp_image.png"))
    os.remove("image_commands/quote_images/temp/temp_image.png")


async def grey_quote_generator(message):
    image_options = ["alex.png", "einstein.png", "ghandi.png", "martinlutherking.png", "motherteresa.png"]
    image = Image.open(f"image_commands/quote_images/greyscale/{image_options[random.randint(0, 4)]}")
    font = ImageFont.truetype("image_commands/quote_images/fonts/CaviarDreams.ttf", 50)

    try:
        quote_message = message.content.split('"')[1]
    except:
        await message.channel.send(embed = await text_commands.embeds.embed_error_message("Must specify a quote author."))

    quote_message = quote_message.strip(" ")
    quote_message_split = quote_message.split(" ")
    chars_on_this_line = 0
    max_chars_per_line = 20
    quote_message_wrap = ""
    for word in quote_message_split:
        quote_message_wrap += word + " "
        chars_on_this_line += len(word)
        if chars_on_this_line >= max_chars_per_line:
            quote_message_wrap = quote_message_wrap + "\n"
            chars_on_this_line = 0

    quote_person = message.content.split('"')[3]
    quote = f'"{quote_message_wrap}" \n         -{quote_person}'

    image_with_message = ImageDraw.Draw(image)
    image_with_message.text((800, 200), quote, (180, 180, 180), font=font)

    image.save("image_commands/quote_images/temp/temp_image.png") 
    await message.channel.send(file=discord.File("image_commands/quote_images/temp/temp_image.png"))
    os.remove("image_commands/quote_images/temp/temp_image.png")

