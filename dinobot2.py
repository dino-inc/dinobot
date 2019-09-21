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



initial_extensions = ['cogs.fun', 'cogs.selfroles', 'cogs.owner', 'cogs.emoji']
#unloaded cogs: adventure, image, stats, chatbot

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
    #await scan_message(message)
    await bot.process_commands(message)

# leaving logging as main code because... might as well
@bot.event
async def on_message_delete(message):
    if message.author.bot == True:
        return
    if message.channel == bot.get_channel(ushankanation):
            botlog = message.guild.get_channel(475865143520133140)
            await log_message(message, botlog)
            print("Logged message in Ushanka's server.")
            return
    elif message.guild == bot.get_guild(rbnr):
        botlog = message.guild.get_channel(345003652521525258)
        await log_message(message, botlog)
        print("Logged message in RBNR.")
    # elif message.guild == bot.get_guild(vault_city):
    #     botlog = message.guild.get_channel(477970043855044623)
    #     await log_message(message, botlog)



@bot.event
async def on_member_remove(member):
    if member.guild != bot.get_guild(rbnr):
        return
    botlogs = discord.utils.get(bot.get_guild(rbnr).channels, name='bot_logs')
    em = discord.Embed(title=member.display_name+' left!', description=member.name+" left. Their ID is "+str(member.id), colour=0xFF0000)
    em.set_author(name=member, icon_url=member.avatar_url)
    em.set_footer(text=time.strftime("%e %b %Y %H:%M:%S%p"))
    await botlogs.send(embed = em)
    print("Logged member who left.")

# @bot.command()
# async def indexGuild(ctx):
#     guild_list_index = []
#     await ctx.send('Beginning indexing, this will take a long time.')
#     for channel in ctx.guild.text_channels:
#         try:
#             async with channel.typing():
#                 tempHist = await channel.history(limit=None,reverse=True).flatten()
#                 guild_list_index.append(tempHist)
#                 print(f'Finished with {channel.name}.')
#         except:
#             print(f'Errored on {channel.name}.')
#     bot.guild_list_index = guild_list_index
#     await ctx.send('Finished indexing the server.')

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
'''
async def scan_message(message):
    global delete_notsobot
    if message.guild == None:
        return
    if message.guild.id == plat_server:
        plat_nsfw_id = 547267129326698497
        if message.author.id == 439205512425504771 and delete_notsobot == True:
            await message.delete()
            delete_notsobot = False
            return
        if ".image" not in message.content:
            return
        banned_words = open("bad.txt", "r").read().split("\n")
        responses = open("responses.txt", "r").read().split("\n")
        stripped = message.content.replace('.image', '')
        stripped = stripped.lower()
        stripped = stripped.split()
        for word in stripped:
            if word in banned_words:
                plat_nsfw = message.guild.get_channel(plat_nsfw_id)
                # embed message itself
                em = discord.Embed(description=message.content,
                                   colour=0xFF0000, timestamp=message.created_at)
                em.set_author(name='Naughty post by: ' + message.author.display_name,
                              icon_url='http://rottenrat.com/wp-content/uploads/2011/01/Marty-Rathbun-anti-sign.jpg')
                em.set_thumbnail(url=message.author.avatar_url)
                em.set_footer(text=f"Posted in #{message.channel.name}")
                # embed url images
                try:
                    attach = message.attachments
                    em.set_image(url=attach[0].url)
                except:
                    pass
                await message.channel.send(random.choice(responses))
                await message.delete()
                await plat_nsfw.send(embed=em)
                await plat_bass.send(embed=em)
                delete_notsobot = True
                return
'''

# dino_bot
token = open("token.txt", 'r')
token = token.read().strip()
bot.run(token, bot=True, reconnect=True)

