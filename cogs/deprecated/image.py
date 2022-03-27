import discord
from discord.ext import commands
import PIL
import aiohttp
import asyncio

class ImageManip:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="some image command.")
    @commands.cooldown(rate=1, per=5)
    async def test(self, ctx, link1):
        await fetch_img_from_link(link1)
        image = Image(filename='image.jpg')
        out = image.point(lambda i: i * 1.2)
        with open("image.jpg", "wb") as f:
            f.write(out)
        await ctx.send(file=discord.File('image.jpg'))





def setup(self):
    self.add_cog(ImageManip(self))

async def fetch_img(session, url):
  with aiohttp.Timeout(10):
    async with session.get(url) as response:
      assert response.status == 200
      return await response.read()

async def fetch_img_from_link(image_url):
    loop = asyncio.get_event_loop()
    async with aiohttp.ClientSession(loop=loop) as session:
        img = loop.run_until_complete(
            fetch_img(session, image_url))
        async with open("image.jpg", "wb") as f:
            f.write(img)



