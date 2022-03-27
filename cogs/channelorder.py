import discord
import json
import asyncio
from discord.ext import tasks, commands
import os

class ChannelOrder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_move_occuring = False
        self.channel_diff_numbers = list()
        # Ignores a number of channel updates, in order to limit the number of notifications to one
        # Contains the json docs of all guild channel logs
        # self.guild_channel_order = dict()


    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        samsara_id = 309168904310095886
        # No position change occurred
        if(before.position == after.position):
            return
        # Feature locked to samsara
        if(before.guild.id != samsara_id):
            return
        # Collect all events and see which is largest
        self.channel_diff_numbers.append((abs(before.position - after.position), before, after))
        if(self.channel_move_occuring == False):
            await check_channel_move(self)
        # print (f"{before.name} in position {before.position} just changed to {after.position}.)")

async def check_channel_move(self):
    self.channel_move_occuring = True
    dino_channel_id = 409569842752913419
    await asyncio.sleep(.5)
    self.channel_diff_numbers = sorted(self.channel_diff_numbers,  key=lambda tup: tup[0])
    changed_channel = self.channel_diff_numbers[-1][1]
    dino_channel = discord.utils.get(changed_channel.guild.channels, id=dino_channel_id)
    await dino_channel.send(f"<#{changed_channel.id}> changed from {changed_channel.position} to {self.channel_diff_numbers[-1][2].position}")
    print(f"<#{changed_channel.id}> changed from {changed_channel.position} to {self.channel_diff_numbers[-1][2].position}")
    self.channel_move_occuring = False
    self.channel_diff_numbers.clear()


def setup(bot):
    bot.add_cog(ChannelOrder(bot))

