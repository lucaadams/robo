import discord
import random
import os
import io
import textwrap
from PIL import Image, ImageDraw, ImageFont

import text_module.embeds


class MissingQuoteMessageError(Exception):
    """ raised if user has not specified a message for their quote """
    pass


class Quote:
    """ used to initialize all of the quote-related fields, put all the fields together in a BytesIO object (which acts like a file but is stored in memory) and send it on discord """
    def __init__(self, message, image_options, image, font, quote_location_x, quote_location_y, font_colour, max_chars_per_line):
        self.message = message

        try:
            self.quote_message = message.content.split('"')[1]
        except:
            raise MissingQuoteMessageError("Need to specify a quote message.")

        try:
            self.quote_author = message.content.split('"')[3]
        except:
            self.quote_author = ""

        self.image_options = image_options
        self.image = image
        self.font = font
        self.quote_location_x = quote_location_x
        self.quote_location_y = quote_location_y
        self.font_colour = font_colour
        self.max_chars_per_line = max_chars_per_line
        self.quote_message_wrap = text_wrap(
            self.quote_message, self.max_chars_per_line)
        self.image_file = io.BytesIO()
        self.quote_content = self.get_quote_content()

    def get_quote_content(self):
        """ gets the message that will go inside the quote """
        if self.quote_author == "":
            return f'"{self.quote_message_wrap}"'
        else:
            return f'"{self.quote_message_wrap}" \n                    - {self.quote_author}'

    async def send_quote(self):
        await self.message.channel.send(file=discord.File(self.image_file, "image.png"))

    async def generate_quote(self):
        """ puts together all the pieces of the quote like the image, content, font etc., puts them together and saves it in a BytesIO object stored in memory. """
        image_with_message = ImageDraw.Draw(self.image)
        image_with_message.text((self.quote_location_x, self.quote_location_y), self.quote_content, (
            self.font_colour, self.font_colour, self.font_colour), font=self.font)
        self.image.save(self.image_file, "PNG")
        self.image_file.seek(0)

        await self.send_quote()


async def execute_quote_command(message):
    try:
        image_type = message.content.split(" ")[2]
    except:
        await message.channel.send(embed=text_module.embeds.embed_error_message("Incomplete command."))

    if image_type == "colour":
        image_options = ["flowerfield1.png", "flowerfield2.png",
                         "flowerfield3.png", "rainbow.png", "sky.png"]
        image = Image.open(
            f"res/quote_images/colourful/{image_options[random.randint(0, 4)]}")
        font = ImageFont.truetype(
            "res/quote_images/fonts/Kiss_Boom.ttf", 130)

        try:
            new_quote = Quote(message, image_options, image, font, 300, 200, 0, 25)
        except MissingQuoteMessageError:
            await message.channel.send(embed=text_module.embeds.embed_error_message("Must specify a quote message."))

        await new_quote.generate_quote()

    elif image_type == "grey":
        image_options = ["alex.png", "einstein.png", "ghandi.png",
                         "martinlutherking.png", "motherteresa.png"]
        image = Image.open(
            f"res/quote_images/greyscale/{image_options[random.randint(0, 4)]}")
        font = ImageFont.truetype(
            "res/quote_images/fonts/CaviarDreams.ttf", 50)

        try:
            new_quote = Quote(message, image_options, image, font, 800, 200, 180, 20)
        except MissingQuoteMessageError:
            await message.channel.send(embed=text_module.embeds.embed_error_message("Must specify a quote message."))

        await new_quote.generate_quote()

    else:
        await message.channel.send(embed=text_module.embeds.embed_error_message("You must specify a valid image type ('grey' or 'colour')"))


def text_wrap(quote_message, max_chars_per_line):
    quote_message = quote_message.strip(" ")
    quote_message_split = quote_message.split(" ")
    chars_on_this_line = 0

    quote_message_wrap = ""

    for word in quote_message_split:
        quote_message_wrap += word + " "
        chars_on_this_line += len(word)
        if chars_on_this_line >= max_chars_per_line:
            if len(quote_message_wrap) < len(quote_message):
                quote_message_wrap += "\n"
                chars_on_this_line = 0

    quote_message_wrap = quote_message_wrap.strip(" ")

    return quote_message_wrap
