import discord
from discord.ext import commands
import wand
from wand.image import Image
import aiohttp


class ImageManip:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="some image command.")
    @commands.cooldown(rate=1, per=5)
    async def magic(self, ctx, scale, image_link):
        await fetch_img_from_link(image_link)
        image = Image(filename='image.jpg')
        success = True
        with image.clone() as liquid:
            try:
                liquid.liquid_rescale(width=int(liquid.width * 0.5), height=int(liquid.height * 0.5),
                                 delta_x=int(0.5 * scale) if scale else 1, rigidity=0)
                liquid.liquid_rescale(width=int(liquid.width * 1.5), height=int(liquid.height * 1.5),
                                 delta_x=scale if scale else 2, rigidity=0)
                liquid.save(filename='image.jpg')
            except:
                success = False
                await ctx.send("Stand by while I analyze the success profile of the command. Error! Not a number!"
                               " Did you enjoy this witticism?")
        if success:
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
    with aiohttp.ClientSession(loop=loop) as session:
        img = loop.run_until_complete(
            fetch_img(session, image_url))
        with open("image.png", "wb") as f:
            f.write(img)



