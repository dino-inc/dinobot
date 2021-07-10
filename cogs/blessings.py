import discord
import sys, traceback
import json
from discord.ext import commands

class Blessings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        try:
            self.blessing_list = json.load(open('blessings.json'))
        except:
            print("Failed to load blessings.")

    def check_if_samsara(ctx):
        return ctx.guild.id == 309168904310095886

    @commands.check(check_if_samsara)
    @commands.command()
    async def bless(self, ctx, member: discord.Member):
        blessing_role = self.blessing_list.get(str(ctx.author.id))
        if blessing_role is not None:
            blessing_role_object = discord.utils.get(ctx.guild.roles, id=int(blessing_role))
            if blessing_role_object not in member.roles:
                await member.add_roles(blessing_role_object)
                await ctx.send(f"Added your blessing role to {member.display_name}.")
            else:
                await member.remove_roles(blessing_role_object)
                await ctx.send(f"Removed your blessing role from {member.display_name}.")
        else:
            await ctx.send("You do not appear to have a blessing role, sorry.")

    # Created solely to compile the roles once
    '''
    @commands.command()
    async def blessrole(self, ctx):
        await ctx.send("compiling blessing roles")
        blessobject = {}
        for role in ctx.guild.roles:
            if "Blessings" in role.name:
                blessobject[role.name] = role.id
        with open('blessings.json', 'w') as blessings:
            json.dump(blessobject, blessings)
    '''


def setup(self):
    self.add_cog(Blessings(self))