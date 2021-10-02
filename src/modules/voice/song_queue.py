import time
import math
import discord

from data import data
import verbose.embeds


emoji_list = ["⏪", "◀️", "⏹️", "▶️", "⏩"]
songs_per_page = 12


class InvalidQueueParameters(Exception):
    """Raised if a queue cannot be found with the parameters passed in"""


class Song:
    def __init__(self, youtube_metadata: dict=None, name: str=None, url: str=None):
        if youtube_metadata is not None:
            self.name = youtube_metadata["title"]
            self.url = youtube_metadata["webpage_url"]
            self.youtube_metadata = youtube_metadata
        else:
            self.name = name
            self.url = url
            self.youtube_metadata = {}


class QueueMessage:
    def __init__(self, message, queue: list[Song]=None, queue_name=None):
        self.queue = queue
        self.name = queue_name if queue_name else "Up next"
        self.message: discord.Message = None
        self.channel = message.channel
        self.current_page = 0
        self.page_count = 0 if queue is None else math.ceil(len(queue) / songs_per_page)
        self.pages: list[str] = []
        if self.page_count != 0:
            self.init_pages()
        self.time_sent = time.time()


    def init_pages(self):
        queue_copy = self.queue.copy()
        for page_num in range(self.page_count):
            page_desc = ""
            for i in range(songs_per_page):
                if len(queue_copy) == 0:
                    break
                song_to_add = queue_copy.pop(0)
                page_desc += f"{i + page_num * songs_per_page + 1} - [{song_to_add.name}]({song_to_add.url})\n"

            self.pages.append(page_desc)


    async def send(self):
        if self.page_count == 0:
            self.message = await self.channel.send(embed=verbose.embeds.embed_response_without_title("Your queue is currently empty."))
        else:
            self.message = await self.channel.send(embed=self.queue_embed())

            for emoji in emoji_list:
                await self.message.add_reaction(emoji)


    async def change_page(self, reaction):
        if self.page_count == 0:
            return

        if reaction.emoji == emoji_list[0]:
            self.current_page = 0

        if reaction.emoji == emoji_list[1]:
            self.current_page -= 1 if self.current_page != 0 else self.page_count - 1

        if reaction.emoji == emoji_list[2]:
            await self.clear_reactions()

        if reaction.emoji == emoji_list[3]:
            self.current_page += 1 if self.current_page != self.page_count - 1 else 0

        if reaction.emoji == emoji_list[4]:
            self.current_page = self.page_count - 1

        await self.message.edit(embed=self.queue_embed())


    async def clear_reactions(self):
        await self.message.clear_reactions()


    def queue_embed(self):
        queue_embed = discord.Embed(
            title = f":information_source: {self.name}:",
            colour = discord.Colour(0x3f87a1),
            description = f"{self.pages[self.current_page]}",
        )
        queue_embed.set_footer(text=f"Page {self.current_page + 1}/{self.page_count}")

        return queue_embed
