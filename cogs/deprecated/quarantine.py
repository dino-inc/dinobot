import discord
from discord.ext import commands
import asyncio
import random

class Fun(commands.Cog):
    def __init__(self, bot):
        example = 1
        
    @commands.command()
    async def infinitetyping(self, ctx, channel : discord.TextChannel):
        print("Excessively long typing begins.")
        async with channel.typing():
            await asyncio.sleep(100000)
            await ctx.send(f"Finished annoying people in {channel.name}.")
            print("Finished long typing.")

    @commands.command()
    async def quarantinehouse(self, ctx, housegroups):
        members = ctx.guild.members
        quarantinelist = []
        membercount = 0
        housegroups = int(housegroups)
        exclusionlist = ["Knyght of Nine","Joey (Inactive)","Thanks Thanos (Joey)","Old Sport","Orea","SoomufuBoy","carcinogenesis","richard blast","Trovolopagus","jesus","Tea","Valta","Etch"]
        for member in members:
            if member.bot:
                continue
            if member.name in exclusionlist:
                continue
            quarantinelist.append(member)
            membercount = membercount + 1
        print(f"Collected {membercount} members.")
        housecontainer = []
        membersAdded = 0
        random.seed(1)
        for y in range(0, housegroups):
            housecontainer.append([])
        while membersAdded != membercount:
            for y in range(0, housegroups):
                if membersAdded != membercount:
                    randomMember = random.choice(quarantinelist)
                    housecontainer[y].append(randomMember)
                    quarantinelist.remove(randomMember)
                    membersAdded = membersAdded + 1
        quarantinehousestring = ""
        for y in range(0, housegroups):
            quarantinehousestring = ""
            quarantinehousestring += f"Quarantine House {y+1}\n"
            for member in housecontainer[y]:
                quarantinehousestring += f"{member.name}\n"
            await ctx.send(quarantinehousestring)


def setup(bot):
    bot.add_cog(Fun(bot))