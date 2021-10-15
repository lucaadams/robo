import time
import math
import discord

import verbose.embeds


class PagedMessage:
    def __init__(self, message_to_reply_to, name, content: list=None, items_per_page=12):
        self.content = content
        self.name = name
        self.message: discord.Message = None # the message itself once sent
        self.channel = message_to_reply_to.channel
        self.current_page = 0
        self.page_count = 0 if content is None else math.ceil(len(content) / items_per_page)
        self.items_per_page = items_per_page
        self.pages: list[str] = []
        if self.page_count != 0:
            self.init_pages()

        self.emoji_list = ["⏪", "◀️", "⏹️", "▶️", "⏩"]
        self.disable_reactions = False if self.page_count > 1 else True # no reactions if only 1 page

        self.time_sent = time.time()


    def init_pages(self):
        content_copy = self.content.copy()
        for i in range(self.page_count):
            page_desc = ""
            for j in range(self.items_per_page):
                if len(content_copy) == 0: # break if no more content
                    break
                item_to_add = content_copy.pop(0)
                page_desc += str(item_to_add)

            self.pages.append(page_desc)


    async def send(self):
        """
        default sending behaviour
        can be overriden
        """
        if self.page_count == 0:
            self.message = await self.channel.send(embed=verbose.embeds.embed_response_without_title("Nothing to display."))
        else:
            self.message = await self.channel.send(embed=self.content_embed())

            if self.page_count > 1:
                for emoji in self.emoji_list:
                    await self.message.add_reaction(emoji)


    async def change_page_internal(self, reaction):
        """
        default page changing behaviour
        can be overriden
        """
        if self.page_count == 0:
            return

        if reaction.emoji == self.emoji_list[0]:
            self.current_page = 0

        if reaction.emoji == self.emoji_list[1]:
            self.current_page -= 1 if self.current_page != 0 else self.page_count - 1

        if reaction.emoji == self.emoji_list[2]:
            self.disable_reactions = True
            await self.clear_reactions()

        if reaction.emoji == self.emoji_list[3]:
            self.current_page += 1 if self.current_page != self.page_count - 1 else 0

        if reaction.emoji == self.emoji_list[4]:
            self.current_page = self.page_count - 1

        await self.message.edit(embed=self.content_embed())


    async def change_page(self, reaction):
        if not self.disable_reactions:
            await self.change_page_internal(reaction)


    async def clear_reactions(self):
        await self.message.clear_reactions()


    def content_embed(self):
        content_embed = discord.Embed(
            title = f":information_source: {self.name}:",
            colour = discord.Colour(0x3f87a1),
            description = f"{self.pages[self.current_page]}",
        )
        if self.page_count > 1:
            content_embed.set_footer(text=f"Page {self.current_page + 1}/{self.page_count}")

        return content_embed
