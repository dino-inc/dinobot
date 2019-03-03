import discord
from discord.ext import commands
import random
import unicodedata
# from sqlalchemy import *
import asyncio
# import requests
import aiohttp
from discord import Webhook, AsyncWebhookAdapter
import os


class Fun(commands.Cog):
    def __init__(self, bot):
        global rbnr
        global pending_game
        global ongoing_game
        global original_member
        global second_member
        self.bot = bot
        rbnr = 231614904035966984
        pending_game = False
        ongoing_game = False
        original_member = None
        second_member = None

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

    # @commands.command(help="Creates the database.")
    # async def databasecreate(self, ctx):
    #     db = create_engine('sqlite:///wordlists.db')
    #
    #     db.echo = False  # Try changing this to True and see what happens
    #
    #     metadata = BoundMetaData(db)
    #
    #     users = Table('users', metadata,
    #                   Column('weapon_action', String, primary_key=True),
    #                   Column('weapon_type', String(40)),
    #                   Column('age', Integer),
    #                   Column('password', String),
    #                   )
    #     users.create()
    #
    #     i = users.insert()
    #     i.execute(name='Mary', age=30, password='secret')
    #     i.execute({'name': 'John', 'age': 42},
    #               {'name': 'Susan', 'age': 57},
    #               {'name': 'Carl', 'age': 33})
    #
    #     s = users.select()
    #     rs = s.execute()

    @commands.command()
    async def infinitetyping(self, ctx, channel : discord.TextChannel):
        print("Excessively long typing begins.")
        async with channel.typing():
            await asyncio.sleep(100000)
            await ctx.send(f"Finished annoying people in {channel.name}.")
            print("Finished long typing.")

    # @commands.command()
    # async def randomquote(self, ctx):
    #     this_dir = os.path.dirname(__file__)
    #     this_dir.replace('/cogs', '')
    #     quote = random.choice(open('quotes.txt').readlines())
    #     await ctx.send(quote)

    @commands.command()
    async def fencewars(self, ctx, member : discord.Member):
        global pending_game
        global original_member
        global second_member
        if pending_game or ongoing_game:
            await ctx.send ("There's a game going on right now, please wait for it to finish.")
            return
        print("Started a needlessly complex game.")
        await ctx.send(f"<@{ctx.author.id}> has challenged <@{member.id}> to a fence war! Type !accept to accept"
                       f" or !surrender to give up.")
        original_member = ctx.author
        second_member = member
        pending_game = True

    @commands.command()
    async def accept(self, ctx):
        global pending_game
        global ongoing_game
        if second_member != ctx.author:
            await ctx.send("You haven't been challenged, try !fencewars [user].")
            return
        elif ongoing_game:
            await ctx.send ("There's a game going on right now, please wait for it to finish.")
            return
        elif pending_game:
            self.bot.game = FenceGame(ctx, original_member, second_member)
            pending_game = False
            ongoing_game = True
            await ctx.send("The ultimate contest of ~~gambling~~ skill has begun! \n\n"
                           f"{original_member.display_name}, please use !work [number < 5].")
        else:
            await ctx.send("Challenge someone with !fencewars first!")
            return

    @commands.command()
    async def surrender(self, ctx):
        global pending_game
        if ongoing_game:
            await ctx.send ("There's a game going on right now, please wait for it to finish.")
            return
        elif pending_game:
            pending_game = False
            await ctx.send("You have cowardly run away from the glory of Fence Wars!")
            return
        elif second_member != ctx.author:
            await ctx.send("You haven't been summoned to participate in a battle.")
            return

    @commands.command()
    async def work(self, ctx, slave_wager: int):
        current = await self.bot.game.get_current()
        if ctx.author is not current.get_member():
            await ctx.send("It is not your turn.")
            return
        await self.bot.game.advance_turn(ctx, slave_wager)


class FenceGame:
    def __init__(self, ctx, member, second_member):
        self.running_game = False
        self.player_one = FenceGamePlayer(member)
        self.player_two = FenceGamePlayer(second_member)
        self.current_player = self.player_one

    async def advance_turn(self, ctx, slave_wager):
        slavecount = self.current_player.get_slaves()
        if slave_wager > slavecount:
            await ctx.send("Please send to work only slaves that you currently have.")
            return
        elif slave_wager < 1:
            await ctx.send("You must send to work at least one slave.")
            return
        await self.choose_event(ctx, slave_wager, self.current_player, self.player_one, self.player_two)
        await self.win_check(ctx, self.player_one, self.player_two)
        if ongoing_game == False:
            return
        await self.switch_turn()

    async def get_current(self):
        return self.current_player
    async def switch_turn(self):
        if self.current_player == self.player_one:
            self.current_player = self.player_two
        else:
            self.current_player = self.player_one

    async def win_check(self, ctx, player_one, player_two):
        global ongoing_game
        if player_one.get_score() > 100:
            ongoing_game = False
            await ctx.send(f"__**{player_one.get_name()} wins!**__"
                           f"\n {player_one.get_name()} has built their fence past 100 meters, with {player_one.get_slaves()} slaves "
                           f"and a final length of {player_one.get_score()}. {player_two.get_name()} came in last place, with "
                           f"{player_two.get_slaves()} slaves and a shorter fence of {player_two.get_score()} meters.")
        elif player_two.get_score() > 100:
            ongoing_game = False
            await ctx.send(f"__**{player_two.get_name()} wins!**__"
                           f"\n {player_two.get_name()} has built their fence past 100 meters, with {player_two.get_slaves()} slaves "
                           f"and a final length of {player_two.get_score()}. {player_one.get_name()} came in last place, with "
                           f"{player_one.get_slaves()} slaves and a shorter fence of {player_one.get_score()} meters.")

    async def current_score(self, player_one, player_two):
        return f"\n**{player_one.get_name()} has {player_one.get_score()} meters of fence and {player_one.get_slaves()}" \
               f" slaves, while {player_two.get_name()} " \
               f"has  {player_two.get_score()} meters of fence and {player_two.get_slaves()} slaves.**"

    async def choose_event(self, ctx, slave_wager, current_player, player_one, player_two):
        other_player = player_two
        if current_player == player_two:
            other_player = player_one
        number = random.randint(0,20)
        if number == 20:
            current_player.add_slaves(current_player.get_slaves())
            current_player.add_score(slave_wager*2)
            fence_score = await self.current_score(player_one, player_two)
            await ctx.send("Your slaves break into a previously undiscovered vault of growth hormones, causing "
                           "them to undergo spontaneous asexual reproduction. Total slave count is doubled, and "
                           f"fence construction proceeds twice as fast. {fence_score}")
        elif number == 19:
            raided_slaves = other_player.get_slaves()/2
            current_player.add_slaves(raided_slaves)
            other_player.remove_slaves(raided_slaves)
            fence_score = await self.current_score(player_one, player_two)
            await ctx.send("Well, **fence**y that. Your slaves raid your opponent's slave camps, enslaving half of them"
                           f" (but getting no work done.) {fence_score}")
        elif number == 18:
            current_player.add_slaves(10)
            current_player.add_score(slave_wager)
            fence_score = await self.current_score(player_one, player_two)
            await ctx.send("The US military shows up with helicopters and pre-built fence parts, dropping down 10 " 
                           f"meters of fencing and some more slaves, while your other slaves toil away. {fence_score}")
        elif number == 17:
            current_player.add_score(slave_wager + 5)
            current_player.add_slaves(5)
            fence_score = await self.current_score(player_one, player_two)
            await ctx.send(f"A violent and bloody revolution occurs, in which the slaves decide democratically among"
                           f" themselves that they should continue working for you, and bring in independent contractors "
                           f"to build even more fence. {fence_score}")
        elif number == 16:
            current_player.add_slaves(10)
            current_player.add_score(slave_wager + 7)
            fence_score = await self.current_score(player_one, player_two)
            await ctx.send(f"Your slaves discover a novel method of quantum entanglement that also happens to be able "
                           f"to make a portal to the slave dimension. Naturally, you agree. {fence_score}")
        elif number == 15:
            current_player.remove_slaves(slave_wager)
            current_player.add_score(slave_wager)
            fence_score = await self.current_score(player_one, player_two)
            await ctx.send(f"You manage to permanently fuse all of your working slaves into the fence... admittedly, using "
                           f"metal plates for protecting the welders was not the smartest. At least they'll make some "
                           f"great halloween decorations. {fence_score}")
        elif number == 14:
            current_player.add_score(slave_wager)
            current_player.add_slaves(5)
            fence_score = await self.current_score(player_one, player_two)
            await ctx.send(f"You decide to pay your slaves, making them your employees. They are quick to"
                           f" demand full health coverage and a retirement plan - needless to say, you won't be trying "
                           f"that again. Sometimes, slaves just don't know what's good for them. You did "
                           f"recruit a few more slaves through online ads, though... they don't seem to be very happy"
                           f" about it.{fence_score}")
        elif number == 13:
            current_player.add_score(slave_wager)
            current_player.add_slaves(10)
            fence_score = await self.current_score(player_one, player_two)
            await ctx.send(f"A hundred thousand cries ring out and are silenced. A coin drops. A dog whimpers. Your slaves "
                           f"toil away, oblivious to a random string of events that would coalesce into the next world"
                           f" war. You also happen to find a mysteriously abandoned bus of 10 slaves. {fence_score}")
        elif number == 12:
            current_player.add_score(slave_wager)
            current_player.remove_slaves(4)
            fence_score = await self.current_score(player_one, player_two)
            await ctx.send(f"The nation you got all these slaves from sends a small army to your encampment to seize "
                           f"their citizens back, but your partially completed fence proves enough to repel the "
                           f"invaders, although they take a few of your slaves' lives. The fence finally had a "
                           f"purpose... although you're not sure why you needed a fence in the first place. {fence_score}")
        elif number == 11:
            current_player.add_score(1)
            fence_score = await self.current_score(player_one, player_two)
            await ctx.send(f"The sun is shining, not a cloud in the sky, and it's a bright summer day. Ideal conditions "
                           f"anywhere but the hard-packed sand and dirt below this new section of the fence. Your air"
                           f" conditioned observation tower mocks the slaves, taunting them as they work under the "
                           f"baking sun. They conspire to secretly take naps... and somehow get away with it. {fence_score}")
        elif number == 10:
            current_player.add_score(slave_wager)
            fence_score = await self.current_score(player_one, player_two)
            await ctx.send(f"It is a perfectly average day for perfectly ordinary slaves to construct generic fences."
                           f" Nothing goes wrong, but nothing goes... right. It's almost as if the bot "
                           f"discovered that you rolled a 10. {fence_score}")
        elif number == 9:
            current_player.add_score(slave_wager + 3)
            current_player.add_slaves(12)
            fence_score = await self.current_score(player_one, player_two)
            await ctx.send(f"The slaves work hard for the entire day, ignoring the odd noises and hallucinations that "
                           f"came about after a strange man was seen poking about in the local well. They accomplish "
                           f"slightly more than normal. Taking count of you slaves later in the day, you notice a "
                           f"strange discrepancy in the number of slaves - you have 12 more than you did the turn before. {fence_score}")
        elif number == 8:
            current_player.remove_slaves(4)
            fence_score = await self.current_score(player_one, player_two)
            await ctx.send(f"Whipping your slaves for their daily obedience training, you notice a lack of pain "
                           f"in one of your slaves. Whipping them harder to experiment with this odd phenomenon, their "
                           f"chest explodes in a crimson mist and dozens of slimy, black alien parasites burst out of"
                           f" the gaping wound. Reeling in horror, you waste your entire turn hunting down and executing "
                           f"the remaining parasites. {fence_score}")
        elif number == 7:
            current_player.remove_slaves(3)
            current_player.add_score(int(slave_wager/3))
            fence_score = await self.current_score(player_one, player_two)
            await ctx.send(f"Digging a foundation for the next fence post, a few of your slaves drop into what seems "
                           f"to be a dilapidated, abandoned testing chamber. A barrage of gunfire ringing out seconds later, "
                           f"you decide to cut your losses for the day and fill the hole with concrete, costing time but "
                           f"avoiding whatever it was you found in the hole. {fence_score}")
        elif number == 6:
            quarter = int(slave_wager/4)
            current_player.add_score(quarter*3)
            fence_score = await self.current_score(player_one, player_two)
            await ctx.send(f"Your slaves discover that one of their own is a terrorist, and organize {quarter} of themselves"
                           f" into counter-terrorism investigations... ignoring their duty to build the fence. {fence_score}")
        elif number == 5:
            current_player.add_score(slave_wager)
            current_player.remove_score(10)
            fence_score = await self.current_score(player_one, player_two)
            await ctx.send(f"Ninten arrives from the wheelchair dimension, clipping into the fence and uprooting 10 meters "
                           f"of it. The slaves are naturally shaken, but continue unafraid of further Ninten events. {fence_score}")
        elif number == 4:
            current_player.add_score(slave_wager)
            fence_score = await self.current_score(player_one, player_two)
            await ctx.send(f"A wild pack of dogs roves between the massive yard of fence nurseries, ripping apart the poor"
                           f" baby fences that had yet to have been planted. No damage is done to the adult fences..."
                           f" just psychological scars that they will take to their rusty grave. {fence_score}")
        elif number == 3:
            current_player.remove_score(1)
            fence_score = await self.current_score(player_one, player_two)
            await ctx.send("Exhausted by the searing sun and the unrelenting, unblinking gaze of the nearby monolithic "
                           f"sculptures of the fence gods, the slaves set down their tools and watch as the statue's "
                           f"long foretold awakening arrives in all its glorious, explosive fury... focused in its "
                           f"entirety on a single section of fence, shunting it into another plane of existfence. "
                           f"{fence_score}")
        elif number == 2:
            current_player.remove_slaves(slave_wager)
            current_player.add_score((slave_wager*2))
            fence_score = await self.current_score(player_one, player_two)
            await ctx.send(f"You slaves toil away, working harder than normal but ignoring all their physical needs, "
                           f" completing their tasks at the cost of their lives. {fence_score}")
        elif number == 1:
            current_player.remove_slaves(slave_wager)
            current_player.remove_score((current_player.get_score()/2))
            fence_score = await self.current_score(player_one, player_two)
            await ctx.send(f"Cataclysmic waves burst out of a rift in time and space, washing away half of your fence "
                           f"and all of your working slaves... although their corpses are well washed. {fence_score}")
        elif number == 0:
            current_player.remove_slaves((current_player.get_slaves()/2))
            current_player.remove_score(20)
            fence_score = await self.current_score(player_one, player_two)
            await ctx.send(f"You discover that several of your slaves have stolen a huge segment of your fence in the night. "
                            f"A lone, cloaked stranger appears over the horizon, accompanied by the faint scent of coffee "
                            f"and a warm breeze. Horrified whispers echo throughout the confines of your slave pits, their "
                            f"disbelief and horror driven further into frenzy by the sight of Punmaster Pakaku slowly lowering his "
                            f"hood. Clearing his throat, silence fell. Five simple, indescribably damaging words emanated "
                            f"from that dread maw - **the slaves... take a fence**. Lungs screaming, mouths frothing, "
                            f"and hands clawing at their flea-bitten ears, half of your slaves die immediately. {fence_score}")
        else:
            current_player.add_slaves(1)
            await ctx.send(f"Something went wrong with the random number generator so... have a free slave. {fence_score}")
class FenceGamePlayer:
    def __init__(self, member):
        self.score = 0
        self.slaves = 5
        self.member_object = member
        self.name = member.display_name
    def get_score(self):
        return self.score
    def get_slaves(self):
        return self.slaves
    def add_score(self, score):
        intscore = int(score)
        self.score += intscore
    def remove_score(self, score):
        intscore = int(score)
        self.score = self.score - intscore
        if self.score < 0:
            self.score = 0
    def add_slaves(self, slave_count):
        intslave = int(self.get_slaves() + slave_count)
        self.slaves = intslave
    def remove_slaves(self, slave_count):
        intslave = int(self.get_slaves() - slave_count)
        self.slaves = intslave
        if self.slaves < 1:
            self.slaves = 1
    def get_name(self):
        return self.name
    def get_member(self):
        return self.member_object
    def set_slaves(self, slaves):
        self.slaves = slaves
def setup(bot):
    bot.add_cog(Fun(bot))