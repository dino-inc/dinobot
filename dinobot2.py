import discord
import time
import sys, traceback
from discord.ext import commands
import random



# time to do this bot again, better this time

bot = commands.Bot(command_prefix='!')

# good variables
owner = 228667580330672128  # straw
azelserver = 309168904310095886  # samsara - maybe woomy's?
rbnr = 231614904035966984  # regs but not regs
ushankanation = 418591546389168129 # ushanka's channel
vault_city = 477880018232672266 #ushanka's server
#plat_server = 292586384957636608 #platinumbass's server

# global variables
bot.guild_list_index = None


def check_if_rbnr(ctx):
    return ctx.guild.id == rbnr

# I hate intents.
intents = discord.Intents.all()


initial_extensions = ['cogs.fun', 'cogs.blessings', 'cogs.emoji', 'cogs.insta', 'cogs.channelorder']
#unloaded cogs: adventure, image, stats, chatbot, owner, selfroles

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
    global plat_bass
    bot.rbnr = rbnr
    # plat_bass = bot.get_guild(plat_server).get_member(292585739642732544)




@bot.event
async def on_message(message):
    # EXTREMELY IMPORTANT DO NOT REMOVE, PROCESSES COMMANDS AFTER CHECKING MESSAGE
    await bot.process_commands(message)

async def log_message(message, botlog):
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
    await botlog.send(embed=em)


# dino_bot
token = open("token.txt", 'r')
token = token.read().strip()
bot.run(token, bot=True, reconnect=True)

