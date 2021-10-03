import discord

import verbose.embeds
from verbose.paged_message import PagedMessage


SONGS_PER_PAGE = 12


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


class QueueMessage(PagedMessage):
    def __init__(self, message_to_reply_to, queue: list[Song]=None, queue_name=None):
        super().__init__(message_to_reply_to, queue_name if queue_name else "Up next", queue, SONGS_PER_PAGE)


    def init_pages(self):
        """override of the super().init_pages() method"""
        queue_copy = self.content.copy()
        for page_num in range(self.page_count):
            page_desc = ""
            for i in range(self.items_per_page):
                if len(queue_copy) == 0:
                    break
                song_to_add = queue_copy.pop(0)
                page_desc += f"{i + page_num * self.items_per_page + 1} - [{song_to_add.name}]({song_to_add.url})\n"

            self.pages.append(page_desc)


    async def send(self):
        """override of the super().send() method"""
        if self.page_count == 0:
            self.message = await self.channel.send(embed=verbose.embeds.embed_response_without_title("Your queue is currently empty."))
        else:
            self.message = await self.channel.send(embed=self.content_embed())

            for emoji in self.emoji_list:
                await self.message.add_reaction(emoji)


    def content_embed(self):
        """override of the super().content_embed() method"""
        queue_embed = discord.Embed(
            title = f":information_source: {self.name}:",
            colour = discord.Colour(0x3f87a1),
            description = f"{self.pages[self.current_page]}",
        )
        queue_embed.set_footer(text=f"Page {self.current_page + 1}/{self.page_count}")

        return queue_embed
