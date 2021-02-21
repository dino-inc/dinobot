import discord
from discord.ext import commands
import pickle

class Emoji(commands.Cog):
    def __init__(self, bot):
        global emoji_channel_id
        global petpoc
        global rbnr
        global tagged
        self.bot = bot
        petpoc = False
        rbnr = 231614904035966984
        emoji_channel_id = 327338669423722507
        tagdump = open("tagged.pickle", "rb")
        tagged = pickle.load(tagdump)
        tagdump.close()

    def check_if_rbnr(ctx):
        return ctx.guild.id == rbnr

    @commands.command(help="Summons the petpocalypse to rain down pets upon your foes.")
    @commands.check(check_if_rbnr)
    async def petpoc(self, ctx):
        global petpoc
        if self.bot.get_guild(rbnr) == ctx.guild and petpoc == False:
            await ctx.send("**PETPOCALYPSE ARISEN**")
            petpoc = True
            print(f"{ctx.author.display_name} toggled the petpocalypse on")
        elif self.bot.get_guild(rbnr) == ctx.guild and petpoc == True:
            await ctx.send("*Petpocalypse powering down...*")
            petpoc = False
            print(f"{ctx.author.display_name} toggled the petpocalypse off")

    @petpoc.error
    async def petpoc_error(self, ctx, error):
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.send("This is not RBNR.")
            print(f"{ctx.author.display_name} tried to toggle the petpocalypse somewhere that wasn't rbnr")
        else:
            await ctx.send("Error. Could not start the petpocalypse. " + str(error))
            print(f"{ctx.author.display_name} toggled the petpocalypse and it failed")

    @commands.command(name='settagged')
    @commands.is_owner()
    async def settagged(self, ctx, member: discord.Member):
        global tagged
        tagged = member.id
        tagged_file_dump = open("tagged.pickle", "wb")
        pickle.dump(tagged, tagged_file_dump)
        tagged_file_dump.close()
        await ctx.send("Tagged "+member.display_name+" with the rainbow.")
        print(f"Set tagged person to {member.display_name}")

    @commands.command(name='checktagged')
    async def checktagged(self, ctx):
        try:
            member = discord.utils.get(ctx.guild.members, id=tagged)
            await ctx.send("The currently tagged user is " + member.display_name + ".")
        except:
            await ctx.send("Sorry, the currently tagged person seems to have vanished.")


    @commands.command()
    async def tag(self, ctx, member: discord.Member):
        global tagged
        if ctx.author.id == tagged:
            tagged = member.id
            pickle.dump(tagged, open("tagged.pickle", "wb"))
            await ctx.send("Tagged "+member.display_name+" with the rainbow.")
        else:
            member = discord.utils.get(ctx.guild.members, id=tagged)
            await ctx.send("You are not "+member.display_name+".")

    @commands.command()
    @commands.is_owner()
    async def emoji_vote(self, ctx, url):
        if ctx.channel.id == emoji_channel_id:
            em = discord.Embed(description="An emoji vote has begun! Press ✅ to vote yes and "
                                           f"❎ to vote no. \n You have 24 hours to vote.",
                               colour=0xFF0000, timestamp=ctx.message.created_at)
            # em.set_author(name=null,
            #               icon_url=null,
            #               url=null)
            em.set_thumbnail(url=url)
            vote_emoji_message = await ctx.send(embed=em)
            await vote_emoji_message.add_reaction("✅")
            await vote_emoji_message.add_reaction("❎")

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
        heck = ":heck:257730871111450625"
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
        if message.guild.id == 309168904310095886:
            sus = ":sus:812872447127846952"
            await check_boi(message, sus, "sus")
            amogus = ":amogus:812872447090098197"
            await check_boi(message, amogus, "amogus")


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        try:
            messageid = payload.message_id
            channelid = payload.channel_id
            reactchannel = self.bot.get_channel(channelid)
            message = await reactchannel.get_message(messageid)
            if payload.emoji.id == 349032980821311488:
                await message.add_reaction("a:animatedpet:393801987247964161")
                print("Added animated pet.")
            elif payload.emoji.id == 251069497241370624:
                await message.add_reaction("a:owowhatsthis:422870186622844937")
                print("Added animated OwO.")
        except: pass

    # quick and dirty emoji id finder
    # async def on_ready(self):
    #     for emoji in self.bot.emojis:
    #         if emoji.name == "fortnitedance":
    #             print(emoji.id)
    #             print(emoji.name)


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
