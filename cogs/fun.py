import discord
from discord.ext import commands
import random
import unicodedata
# from sqlalchemy import *
import asyncio
import re
# import requests
import aiohttp
from discord import Webhook, AsyncWebhookAdapter
import os


class Fun(commands.Cog):
    def __init__(self, bot):
        global pending_game
        global ongoing_game
        global original_member
        global second_member
        self.bot = bot
        pending_game = False
        ongoing_game = False
        original_member = None
        second_member = None


    @commands.Cog.listener()
    async def on_message(self, message):
        regex = re.compile("<@[!,&]([0-9]*)> (?i)cute")
        match = regex.match(message.content)
        try:
            match.group(1)
        except:
            return
        def check(m):
            return int(match.group(1)) == m.author.id
        try:
            response = await self.bot.wait_for("message", check=check, timeout=300)
        except asyncio.exceptions.TimeoutError:
            return
        await message.channel.send(f"<@{message.author.id}> Your password is {response.content}")



    # STATUS

    @commands.command(help="Changes the bot's status.")
    @commands.cooldown(rate=1, per=30)
    async def status(self, ctx, *, arg):
        await self.change_presence(game=discord.Game(name=arg))
        print("Changed status to ", arg)

    @status.error
    async def status_error(self, ctx, error):
        if isinstance(error, commands.errors.CommandOnCooldown):
            await ctx.send(
                "Please wait {0} seconds before using this command again.".format(format(error.retry_after, '.2f')))
            print(f"Forced a cooldown on {ctx.author.display_name}")
        else:
            await ctx.send("Error. Could not change status.")
            print(f"Status could not be changed at the request of {ctx.author.display_name}")

    @commands.command(help = "Fun with RNG.")
    async def luckynumber(self, ctx):
        random.seed(a=ctx.author.id)
        await ctx.send('Your lucky number is ' + str(int(round(random.random()*100, 0))) +".")
        print(f"Gave a lucky number to {ctx.author.display_name}")

    @commands.command(help = "Rating system.")
    async def rate(self, ctx):
        print(f"Rated {ctx.author.display_name}")
        if ctx.message.content == "-rate dino":
            await ctx.send('I give that a 101/100!!!')
            return
        if ctx.message.content == "-rate spinny":
            await ctx.send('I give that a nice hug!')
            return
        rngseed = 0
        for x in list(ctx.message.content):
            temp = ord(x)
            if temp % 2 == 0:
                rngseed += ord(x)
            else:
                rngseed *= ord(x)
        random.seed(a=rngseed)
        rating = int(round(random.random() * 100, 0))
        if rating < 51:
            await ctx.send('I give that a ' + str(rating) + "/100.")
        else:
            await ctx.send('I give that a ' + str(rating) + "/100!")


    @commands.command()
    async def infinitetyping(self, ctx, channel : discord.TextChannel):
        print("Excessively long typing begins.")
        async with channel.typing():
            await asyncio.sleep(100000)
            await ctx.send(f"Finished annoying people in {channel.name}.")
            print("Finished long typing.")

def setup(bot):
    bot.add_cog(Fun(bot))