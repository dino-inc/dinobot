import discord
from discord.ext import commands


class SelfRoles:
    def __init__(self, bot):
        global owner
        global rbnr
        global selfrolelist
        self.bot = bot
        owner = 141695444995670017  # dino
        rbnr = 231614904035966984  # regs but not regs
        selfrolelist = ['Perverts', 'Dragons and Dungeons', 'Master Debater', 'TF Mercs', 'Overwatch Agent', 'Heisters',
                        "Garry's Mothers", 'Miners', 'Killer of Floors', 'Counter Strike', 'Super Smash Bro',
                        'Town of Salem', 'Team Rainbow', 'Tenno Skoom', 'Inklings', 'Paladins', 'Four Honour', 'Lethal League']

    def check_if_rbnr(ctx):
        return ctx.guild.id == rbnr

    @commands.group(help="Allows you to add roles to yourself.")
    @commands.check(check_if_rbnr)
    async def selfrole(self, ctx):
        pass

    @selfrole.command(description="Adds a role.", help=" - adds a role.")
    async def add(self, ctx, *, role):
        lowerselfrolelist = [x.lower() for x in selfrolelist]
        if role in selfrolelist:
            await add_role_string(ctx, role, selfrolelist)
        elif role in lowerselfrolelist:
            role = selfrolelist[lowerselfrolelist.index(role)]
            await add_role_string(ctx, role, selfrolelist)
        else:
            await ctx.send("That's not a self-assignable role!")

    @selfrole.error
    async def selfrole_error(self, ctx, error):
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.send("This is not RBNR.")
        else:
            await ctx.send("Error. Could not give role.")

    @selfrole.command(description="Removes a role.", help=" - removes a role.")
    async def remove(self, ctx, *, role):
        lowerselfrolelist = [x.lower() for x in selfrolelist]
        if role in selfrolelist:
            await remove_role_string(ctx, role, selfrolelist)
        elif role in lowerselfrolelist:
            role = selfrolelist[lowerselfrolelist.index(role)]
            await remove_role_string(ctx, role, selfrolelist)
        else:
            await ctx.send("That's not a self-removable role!")

    @selfrole.command(invoke_without_subcommand=True, description="Lists the roles", help=" - lists the roles.")
    async def list(self, ctx):
        em = discord.Embed(title='Use !selfrole [add or remove] [role] to modify your roles.',
                           description='\n'.join(selfrolelist), colour=0xFFD700)
        em.set_author(name='Self Assignable Roles')
        await ctx.send(embed=em)


async def add_role_string(ctx, selfrole, list):
    role = discord.utils.get(ctx.guild.roles, name=selfrole)
    if role in ctx.author.roles:
        await ctx.send("You already have this role.")
        return
    await ctx.author.add_roles(role)
    rolesuccess = await ctx.send(
        "The **" + selfrole + "** role has been successfully assigned to **" + ctx.author.name + "**.")


async def remove_role_string(ctx, selfrole, list):
    role = discord.utils.get(ctx.guild.roles, name=selfrole)
    if role not in ctx.author.roles:
        await ctx.send("You don't have this role.")
        return
    await ctx.author.remove_roles(role)
    rolesuccess = await ctx.send(
        "The **" + selfrole + "** role has been successfully removed from **" + ctx.author.name + "**.")


def setup(self):
    self.add_cog(SelfRoles(self))
