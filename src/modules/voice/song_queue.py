import time
import math
import discord

import data
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
        if queue is not None:
            self.queue = queue
        else:
            guild_data = data.get_guild_data(message.guild.id)
            if queue_name not in guild_data["saved_queues"]:
                raise InvalidQueueParameters
            queue = guild_data["saved_queues"][queue_name]

        self.name = queue_name if queue_name else "Current Queue"
        self.message: discord.Message = None
        self.channel = message.channel
        self.current_page = 0
        self.page_count = math.ceil(len(queue) / songs_per_page)
        self.pages: list[str] = []
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
            self.message = await self.channel.send(embed=verbose.embeds.embed_response("Up next", self.pages[0]))

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
            self.current_page += 1 if self.current_page != self.page_count else 0

        if reaction.emoji == emoji_list[4]:
            self.current_page = self.page_count - 1

        await self.message.edit(embed=verbose.embeds.embed_response("Up next", self.pages[self.current_page]))


    async def clear_reactions(self):
        await self.message.clear_reactions()
