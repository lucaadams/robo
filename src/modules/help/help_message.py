import discord

from verbose.paged_message import PagedMessage


ITEMS_PER_PAGE = 6


class HelpMessage(PagedMessage):
    def __init__(self, message_to_reply_to, content: list[str], module_name: str):
        super().__init__(message_to_reply_to, module_name, content, ITEMS_PER_PAGE)

    def content_embed(self):
        """override of the super().content_embed() method"""
        content_embed = discord.Embed(
            title = f":page_with_curl: {self.name}:",
            colour = discord.Colour(0x3f87a1),
            description = f"{self.pages[self.current_page]}",
        )
        content_embed.set_footer(text=f"Page {self.current_page + 1}/{self.page_count}")

        return content_embed
