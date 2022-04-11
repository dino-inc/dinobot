import discord
import sys, traceback
from discord.ext import commands


# time to do this bot again, better this time

bot = commands.Bot(command_prefix='-')

# Samsara ID
azelserver = 309168904310095886

# I hate intents.
intents = discord.Intents.all()

# TODO: Switch from testing mode when rewrite finished
# initial_extensions = ['cogs.fun', 'cogs.blessings', 'cogs.emoji', 'cogs.channelorder', 'cogs.insta']
initial_extensions = ['cogs.emoji']

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

# dino_bot
token = open("token.txt", 'r')
token = token.read().strip()
bot.run(token, bot=True, reconnect=True)

