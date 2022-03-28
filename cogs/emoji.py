import discord
from discord.ext import commands
import pickle

class Emoji(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        global petpoc
        if petpoc == True and self.bot.get_guild(rbnr) == message.guild:
            # called after initial if to improve performance (still not sure if it does)
            petchannel = discord.utils.get(message.guild.channels, name="shitposters_paradise")
            if petchannel == message.channel:
                await message.add_reaction("a:animatedpet:393801987247964161")
        if message.author.id == tagged:
            blobdance = "a:blobdance:429457433707151361"
            await check_boi(message, blobdance, "boi")
        else:
            boi = "a:boi:452994849319419915"
            await check_boi(message, boi, "boi")
        heck = ":heck:830595955417284648"
        await check_boi(message, heck, "heck")
        await check_boi(message, heck, "hecking")
        dab = "a:vault_dab:452284889262325762"
        await check_boi(message, dab, "dab")
        await check_boi(message, dab, "dabbing")
        fortnite = "a:fortnitedance:478779951269675008"
        await check_boi(message, fortnite, "fortnite")
        augh = "a:augh:654202633174777876"
        await check_boi(message, augh, "augh")
        dudewtf = ":dudewtf:650772731742126120"
        await check_boi(message, dudewtf, "smegma")
        moe = ":moe:875565586023874601"
        await check_boi(message, moe, "moe")
        if message.guild.id == 309168904310095886:
            oomfiebateman = ":oomfiebateman:957041584480849980"
            await check_boi(message, oomfiebateman, "oomfie")
            sus = ":sus:812872447127846952"
            await check_boi(message, sus, "sus")
            amogus = ":amogus:812872447090098197"
            await check_boi(message, amogus, "amogus")
            deathpose = ":deathpose:907418831335616552"
            await check_boi(message, deathpose, "gryphon")
            await check_boi(message, deathpose, "gryphonje")


async def check_boi(message, reaction, trigger):
    if trigger in message.content.lower():
        if " "+trigger+" " in message.content.lower():
            await message.add_reaction(reaction)
            await log_reaction_event(trigger)
        elif message.content.lower().startswith(trigger+" ") or message.content.startswith(trigger.upper()+" "):
            await message.add_reaction(reaction)
            await log_reaction_event(trigger)
        elif message.content.lower().endswith(" "+trigger) or message.content.endswith(" "+trigger.upper()):
            await message.add_reaction(reaction)
            await log_reaction_event(trigger)
        elif len(message.content) == len(trigger):
            await message.add_reaction(reaction)
            await log_reaction_event(trigger)

async def log_reaction_event(trigger):
    print(f"Added {trigger} reaction.")

def setup(bot):
    bot.add_cog(Emoji(bot))
