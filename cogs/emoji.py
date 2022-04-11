import json
from discord.ext import commands
import os

class Emoji(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        verify_emoji_json_exists()
        try:
            self.json_emoji_db = json.load(open('emojireactions.json', "r"))
        except json.JSONDecodeError:
            self.json_emoji_db = {"emojis": []}
            print("Error loading emoji db, check emojireactions.json.")

    # TODO: Rewrite emoji reactions
    # TODO: Remove legacy code
    '''
    @commands.Cog.listener()
    async def on_message(self, message):
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
            await check_boi(message, deathpose, "gryphonje")'''

    @commands.command(help = "Input a trigger phrase, the emoji id, and 'opt-in' or 'opt-out'.")
    @commands.is_owner()
    async def add_reaction(self, ctx, trigger_phrase, reaction_emoji_id, opt_status):
        # Handle inserting into empty dict
        if self.json_emoji_db == {}:
            self.json_emoji_db["emojis"] = []

        # Retrieve emoji from server and format for dict
        reaction_str = None
        for emoji in ctx.guild.emojis:
            if emoji.id == int(reaction_emoji_id):
                if not emoji.animated:
                    reaction_str = f"<:{emoji.name}:{reaction_emoji_id}>"
                else:
                    reaction_str = f"<a:{emoji.name}:{reaction_emoji_id}>"
        if reaction_str is None:
            await ctx.send("Emoji not found! Try again?")
            return

        # Check reaction emoji and add trigger phrase to existing entry if possible
        for index, emoji_entry in enumerate(self.json_emoji_db["emojis"]):
            if emoji_entry["reaction"] == reaction_str:
                # Ignore trigger if it's already in dict
                for phrase in emoji_entry["trigger"]:
                    if trigger_phrase == phrase:
                        await ctx.send("Trigger phrase already present for this reaction.")
                        return
                self.json_emoji_db["emojis"][index]["trigger"].append(trigger_phrase)

                # Write updated dict to file
                with open("emojireactions.json", "w+") as output_file:
                    json.dump(self.json_emoji_db, output_file)
                return

        # Convert opt-in to bool
        opt_bool = None
        if opt_status == "opt-in":
            opt_bool = True
        elif opt_status == "opt-out":
            opt_bool = False
        if opt_bool is None:
            await ctx.send("Malformed opt status! Please use *exactly* opt-in or opt-out.")
            return

        # Generate a new dict entry
        self.json_emoji_db["emojis"].append({"trigger": [trigger_phrase],
                                             "reaction": reaction_str,
                                             "opt-in": opt_bool,
                                             "users": []})

        # Write to file immediately
        with open("emojireactions.json", "w+") as output_file:
            json.dump(self.json_emoji_db, output_file)

'''
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
    '''

def verify_emoji_json_exists():
    if os.path.exists('emojireactions.json'):
        return
    else:
        with open('emojireactions.json', 'w') as json_file:
            json.dump({"emojis": []}, json_file)
        return


def setup(bot):
    bot.add_cog(Emoji(bot))
