import json
from discord.ext import commands
import os
import re

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

    @commands.Cog.listener()
    async def on_message(self, message):
        cleaned_msg_content = re.sub('[^a-zA-Z0-9]+', ' ', message.content)
        msg_word_array = cleaned_msg_content.split()
        for emoji_entry in self.json_emoji_db["emojis"]:
            for trigger in emoji_entry["trigger"]:
                if trigger in msg_word_array and message.guild.id == emoji_entry["server"]:
                    if emoji_entry["opt-in"]:
                        if message.author.id not in emoji_entry["users"]:
                            return
                    else:
                        if message.author.id in emoji_entry["users"]:
                            return
                    await message.add_reaction(emoji_entry["reaction"])



    @commands.command(help="Subscribe or unsubscribe to a reaction, based on trigger phrase.", aliases=["unsubscribe"])
    async def subscribe(self, ctx, trigger_phrase):

        for index, emoji_entry in enumerate(self.json_emoji_db["emojis"]):
            for trigger in emoji_entry["trigger"]:
                if trigger == trigger_phrase:
                    user_array = self.json_emoji_db["emojis"][index]["users"]
                    if ctx.author.id not in user_array:
                        user_array.append(ctx.author.id)
                        print(f"Added {ctx.author.display_name} to emoji entry.")
                    else:
                        user_array.remove(ctx.author.id)
                        print(f"Removed {ctx.author.display_name} from emoji entry.")
                    update_reactions_db(self.json_emoji_db)
                    return
        await ctx.send("Could not find that phrase, maybe a typo?")

    @commands.command(help = "Input a trigger phrase, the emoji id, 'opt-in' or 'opt-out', and server if applicable.",
                      aliases=["addreaction"])
    @commands.is_owner()
    async def add_reaction(self, ctx, trigger_phrase, reaction_emoji_id, opt_status):
        # Handle inserting into empty dict
        if self.json_emoji_db == {}:
            self.json_emoji_db["emojis"] = []

        # Retrieve emoji from server and format for dict
        reaction_str = None
        for server in self.bot.guilds:
            for emoji in server.emojis:
                if emoji.id == int(reaction_emoji_id):
                    if not emoji.animated:
                        reaction_str = f":{emoji.name}:{reaction_emoji_id}"
                    else:
                        reaction_str = f"a:{emoji.name}:{reaction_emoji_id}"
        if reaction_str is None:
            await ctx.send("Emoji not found! Maybe the emoji is hosted in a different server?")
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
                update_reactions_db(self.json_emoji_db)
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
                                             "users": [],
                                             "server": ctx.guild.id
                                             })

        # Write to file immediately
        update_reactions_db(self.json_emoji_db)

        await ctx.message.add_reaction(reaction_str)


def verify_emoji_json_exists():
    if os.path.exists('emojireactions.json'):
        return
    else:
        with open('emojireactions.json', 'w') as json_file:
            json.dump({"emojis": []}, json_file)
        return

def update_reactions_db(dict):
    with open("emojireactions.json", "w+") as output_file:
        json.dump(dict, output_file)


def setup(bot):
    bot.add_cog(Emoji(bot))
