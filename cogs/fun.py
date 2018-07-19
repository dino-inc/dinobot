import discord
from discord.ext import commands
import random
import unicodedata
from sqlalchemy import *
import asyncio
import requests
from discord import Webhook, RequestsWebhookAdapter


class Fun:
    def __init__(self, bot):
        global rbnr
        self.bot = bot
        rbnr = 231614904035966984

    def check_if_rbnr(ctx):
        return ctx.guild.id == rbnr


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
        else:
            await ctx.send("Error. Could not change status.")

    @commands.command(help = "Fun with RNG.")
    async def luckynumber(self, ctx):
        random.seed(a=ctx.author.id)
        await ctx.send('Your lucky number is ' + str(int(round(random.random()*100, 0))) +".")

    @commands.command(help = "Rating system.")
    async def rate(self, ctx):
        if ctx.message.content == "!rate dino":
            await ctx.send('I give that a 101/100!!!')
            return
        if ctx.message.content == "!rate spinny":
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
    @commands.command(help="Creates the database.")
    async def databasecreate(self, ctx):
        db = create_engine('sqlite:///wordlists.db')

        db.echo = False  # Try changing this to True and see what happens

        metadata = BoundMetaData(db)

        users = Table('users', metadata,
                      Column('weapon_action', String, primary_key=True),
                      Column('weapon_type', String(40)),
                      Column('age', Integer),
                      Column('password', String),
                      )
        users.create()

        i = users.insert()
        i.execute(name='Mary', age=30, password='secret')
        i.execute({'name': 'John', 'age': 42},
                  {'name': 'Susan', 'age': 57},
                  {'name': 'Carl', 'age': 33})

        s = users.select()
        rs = s.execute()

    @commands.command()
    async def infinitetyping(self, ctx, channel : discord.TextChannel):
        async with channel.typing():
            await asyncio.sleep(120)
            await ctx.send(f"Finished annoying people in {channel.name}.")

    # @commands.command(help="webhook test")
    # async def webhooktest(self, ctx):
    #     webhook = Webhook.partial(123456, 'abcdefg', adapter=RequestsWebhookAdapter())
    #     webhook.send('Hello World', username='Foo')

def setup(bot):
    bot.add_cog(Fun(bot))