import discord
import time
import sys, traceback
from discord.ext import commands



# time to do this bot again, better this time

bot = commands.Bot(command_prefix='!')

# good variables
owner = 141695444995670017  # dino
azelserver = 309168904310095886  # samsara - maybe woomy's?
rbnr = 231614904035966984  # regs but not regs
ushankanation = 418591546389168129 # ushanka's channel
# global variables
bot.guild_list_index = None


def check_if_rbnr(ctx):
    return ctx.guild.id == rbnr


initial_extensions = ['cogs.stats', 'cogs.owner', 'cogs.selfroles', 'cogs.chatbot', 'cogs.fun', 'cogs.emoji',
                      'cogs.adventure']

if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()


@bot.event
async def on_connect():
    print("Connected to Discord.")


@bot.event
async def on_ready():
    print(discord.__version__)
    print('Logged on as {0}!'.format(bot.user.name))
    print('Servers: ', end ='')
    for guild in bot.guilds:
        print(str('{0}, ').format(guild), end='')
    print()
    print("------------------------------")




@bot.event
async def on_message(message):
    # EXTREMELY IMPORTANT DO NOT REMOVE, PROCESSES COMMANDS AFTER CHECKING MESSAGE
    await bot.process_commands(message)

# leaving logging as main code because... might as well
@bot.event
async def on_message_delete(message):
    if message.guild != bot.get_guild(rbnr):
        if message.guild == bot.get_guild(azelserver) and message.channel == bot.get_channel(ushankanation) and message.author.bot != True:
            botlogs = message.guild.get_channel(475865143520133140)

            # I could make this a function and not just ctrl + c but... meh too lazy

            em = discord.Embed(title='Deleted post in #{}'.format(message.channel), description=message.content,
                               colour=0xFFD700)
            em.set_author(name=message.author, icon_url=message.author.avatar_url)
            em.set_footer(text=time.strftime("%e %b %Y %H:%M:%S%p"))
            try:
                if votearrow.content.startswith('https://'):
                    em.set_image(url=message.content)
            except:
                pass
            try:
                attach = message.attachments
                em.set_image(url=attach[0].url)
            except:
                pass
            # sending actual embed
            await botlogs.send(embed=em)
        return
    elif message.author.bot == True:
        return
    else:
        botlogs = message.guild.get_channel(345003652521525258)
        em = discord.Embed(title='Deleted post in #{}'.format(message.channel), description=message.content, colour=0xFFD700)
        em.set_author(name=message.author, icon_url=message.author.avatar_url)
        em.set_footer(text=time.strftime("%e %b %Y %H:%M:%S%p"))
        try:
            if votearrow.content.startswith('https://'):
                em.set_image(url=message.content)
        except:
            pass
        try:
            attach = message.attachments
            em.set_image(url=attach[0].url)
        except:
            pass
    # sending actual embed
        await botlogs.send(embed=em)


@bot.event
async def on_member_remove(member):
    if member.guild != bot.get_guild(rbnr):
        return
    botlogs = discord.utils.get(bot.get_guild(rbnr).channels, name='bot_logs')
    em = discord.Embed(title=member.display_name+' left!', description=member.name+" left. Their ID is "+str(member.id), colour=0xFF0000)
    em.set_author(name=member, icon_url=member.avatar_url)
    em.set_footer(text=time.strftime("%e %b %Y %H:%M:%S%p"))
    await botlogs.send(embed = em)

@bot.command()
async def indexGuild(ctx):
    guild_list_index = []
    await ctx.send('Beginning indexing, this will take a long time.')
    for channel in ctx.guild.text_channels:
        try:
            async with channel.typing():
                tempHist = await channel.history(limit=None,reverse=True).flatten()
                guild_list_index.append(tempHist)
                print(f'Finished with {channel.name}.')
        except:
            print(f'Errored on {channel.name}.')
    bot.guild_list_index = guild_list_index
    await ctx.send('Finished indexing the server.')

# dino_bot
token = open("token.txt", 'r')
bot.run(token.read(), bot=True, reconnect=True)