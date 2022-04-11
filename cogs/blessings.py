import discord
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
    @commands.command(help="Adds or removes your personal blessing role from a member.")
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

    @bless.error
    async def bless_error(self, ctx, error):
        await ctx.send(error)


def setup(self):
    self.add_cog(Blessings(self))