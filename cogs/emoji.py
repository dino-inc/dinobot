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

    @commands.Cog.listener()
    async def on_message(self, message):
        cleaned_msg_content = re.sub('[^a-zA-Z0-9]+', ' ', message.content)
        for emoji_entry in self.json_emoji_db["emojis"]:
            for trigger in emoji_entry["trigger"]:
                match = None
                if trigger in cleaned_msg_content:
                    if message.content == trigger or \
                       message.content.endswith(" "+trigger) or\
                       message.content.startswith(trigger+" "):
                        match = True
                    else:
                        match = re.search(f"(.*\s({trigger})\s.*)", cleaned_msg_content)
                if match and message.guild.id == emoji_entry["server"] and message.author.id != 416391123360284683:
                    if emoji_entry["opt-in"]:
                        if message.author.id not in emoji_entry["users"]:
                            continue
                    else:
                        if message.author.id in emoji_entry["users"]:
                            continue
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
                    await ctx.send("Adjusted your preferences.")
                    return
        await ctx.send("Could not find that phrase, maybe a typo?")

    @commands.group(help = "Lists all reactions for the server.")
    async def list(self, ctx):
        pass

    @list.command(help="The debug version of the list.")
    async def debug(self, ctx):
        output_string = ""
        for emoji_entry in self.json_emoji_db["emojis"]:
            if emoji_entry["server"] == ctx.guild.id:
                output_string += f"{emoji_entry['trigger']} {emoji_entry['reaction']}, opt-in: {emoji_entry['opt-in']}, users: {emoji_entry['users']}\n"
        await send_paginated(ctx, output_string)

    @list.command(help="Show all unsubscribed reactions.")
    async def unsubscribed(self, ctx):
        output_string = "All unsubscribed reactions:\n"
        for emoji_entry in self.json_emoji_db["emojis"]:
            if not is_subscribed(emoji_entry, ctx.author.id, ctx.guild.id):
                formatted_triggers = ", ".join(emoji_entry["trigger"])
                output_string += f"<{emoji_entry['reaction']}>  {formatted_triggers}\n"
        await send_paginated(ctx, output_string)

    @list.command(help="Show all subscribed reactions.")
    async def subscribed(self, ctx):
        output_string = "All subscribed reactions:\n"
        for emoji_entry in self.json_emoji_db["emojis"]:
            if is_subscribed(emoji_entry, ctx.author.id, ctx.guild.id):
                formatted_triggers = ", ".join(emoji_entry["trigger"])
                output_string += f"<{emoji_entry['reaction']}>  {formatted_triggers}\n"
        await send_paginated(ctx, output_string)

    @commands.command(help = "Input a trigger phrase, the emoji id, and 'opt-in' or 'opt-out'.",
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


def update_reactions_db(db):
    with open("emojireactions.json", "w+") as output_file:
        json.dump(db, output_file)


def is_subscribed(emoji, user_id, guild_id):
    if emoji["server"] != guild_id:
        return False
    if emoji["opt-in"] is True and user_id in emoji["users"]:
        return True
    elif emoji["opt-in"] is False and user_id not in emoji["users"]:
        return True
    else:
        return False


async def send_paginated(ctx, text):
    response_chunk = 0
    chunk_size = 1999
    if len(text) > 2000:
        while len(text) > response_chunk:
            await ctx.send(text[response_chunk:response_chunk + chunk_size])
            response_chunk += chunk_size
    else:
        await ctx.send(text)


def setup(bot):
    bot.add_cog(Emoji(bot))
