import discord
from discord.ext import commands
import Pillow

class Image:
    def __init__(self, bot):
        self.bot = bot
        self.rbnr = self.bot.rbnr

    @commands.command(help="Changes the bot's status.")
    @commands.cooldown(rate=1, per=10)
    async def status(self, ctx, image_link):

def setup(self):
    self.add_cog(Image(self))