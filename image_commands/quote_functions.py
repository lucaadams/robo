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
        image_options = ["flowerfield1.png", "flowerfield2.png", "flowerfield3.png", "rainbow.png", "sky.png"]
        image = Image.open(f"image_commands/quote_images/colourful/{image_options[random.randint(0, 4)]}")
        font = ImageFont.truetype("image_commands/quote_images/fonts/Kiss_Boom.ttf", 130)

        await quote_generator(message, image_options, image, font, 300, 200, 0, 20)

    elif image_type == "grey":
        image_options = ["alex.png", "einstein.png", "ghandi.png", "martinlutherking.png", "motherteresa.png"]
        image = Image.open(f"image_commands/quote_images/greyscale/{image_options[random.randint(0, 4)]}")
        font = ImageFont.truetype("image_commands/quote_images/fonts/CaviarDreams.ttf", 50)

        await quote_generator(message, image_options, image, font, 800, 200, 180, 20)

    else:
        await message.channel.send(embed=await text_commands.embeds.embed_error_message("You must specify a valid image type ('grey' or 'colour')"))


async def quote_generator(message, image_options, image, font, quote_location_x, quote_location_y, font_colour, max_chars_per_line):
    try:
        quote_message = message.content.split('"')[1]
    except:
        await message.channel.send(embed=await text_commands.embeds.embed_error_message("Must specify a quote author."))

    quote_message_wrap = await text_wrap(quote_message, max_chars_per_line)

    quote_person = message.content.split('"')[3]
    quote = f'"{quote_message_wrap}" \n                      -{quote_person}'

    image_with_message = ImageDraw.Draw(image)
    image_with_message.text((quote_location_x, quote_location_y), quote, (font_colour, font_colour, font_colour), font=font)

    image.save("image_commands/quote_images/temp/temp_image.png")
    await message.channel.send(file=discord.File("image_commands/quote_images/temp/temp_image.png"))
    os.remove("image_commands/quote_images/temp/temp_image.png")


async def text_wrap(quote_message, max_chars_per_line):
    quote_message = quote_message.strip(" ")
    quote_message_split = quote_message.split(" ")
    chars_on_this_line = 0
    quote_message_wrap = ""
    for word in quote_message_split:
        quote_message_wrap += word + " "
        chars_on_this_line += len(word)
        if chars_on_this_line >= max_chars_per_line:
            quote_message_wrap += "\n"
            chars_on_this_line = 0

    quote_message_wrap = quote_message_wrap.strip(" ")

    return quote_message_wrap

