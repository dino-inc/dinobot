import discord
from discord.ext import commands
import PIL

class Image:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="some image command.")
    @commands.cooldown(rate=1, per=10)
    async def image(self, ctx, image_link):
        await ctx.send('will do later')

def setup(self):
    self.add_cog(Image(self))