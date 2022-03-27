import discord
from discord.ext import commands
import matplotlib.pyplot as plt
from operator import itemgetter
import pickle
import json


class StatCommands:
    def __init__(self, bot):
        global rbnr
        global searching
        global owner
        self.bot = bot
        searching = False
        owner = 141695444995670017  # dino
        rbnr = 231614904035966984  # regs but not regs
        self.stat_index = self.bot.guild_list_index

    @commands.group(help="Comprehensive stats.")
    async def newsearch(self, ctx):
        self.stat_index = self.bot.guild_list_index
        if self.stat_index is None:
            await ctx.send("Cannot generate stats; no index exists. Use !indexGuild to generate one.")
            return

    # @newsearch.error
    # async def newsearch_error(self, ctx, error):
    #     print("errored")
    #     if isinstance(error, commands.errors.MissingRequiredArgument):
    #         await ctx.send("Please enter a valid subcommand. (total or search)")
    #     else:
    #         await ctx.send(error)


    @newsearch.group()
    async def total(self, ctx):
        pass

    # @total.error
    # async def newsearch_total_error(self, ctx, error):
    #     if isinstance(error, commands.errors.MissingRequiredArgument):
    #         await ctx.send("Please enter a valid subcommand. (user, channel, or server)")
    #     else:
    #         await ctx.send(error)

    @total.command()
    async def user(self, ctx, target : discord.Member):
        await ctx.send(embed=await total_user_stats(ctx, target, self.stat_index))

    @total.command()
    async def channel(self, ctx, target : discord.TextChannel):
        await ctx.send(f"Searching for total channel stats on {target.name}.")


# The command graveyard, for purposes of easy access. Will remove later.
    # @commands.command()
    # async def oldsearch(self, ctx, channel, count : int, *, arg):
    #     global searching
    #     if not searching:
    #         if ctx.author.id != owner:
    #             if count > 100000:
    #                 await ctx.send("wtf are you trying to kill me")
    #                 return
    #             elif count > 50000:
    #                 await ctx.send("Try a number lower than 50000.")
    #                 return
    #         searching = True
    #         timegraph = []
    #         axis = []
    #         searchinprogress = await ctx.send("Searching...")
    #         previousdate = str(ctx.message.created_at.day) + str(ctx.message.created_at.month) + str(ctx.message.created_at.year)
    #         dayusecount = 0
    #         daycount = 0
    #         messagecollectedcount = 0
    #         serversearch = False
    #         channel = discord.utils.get(ctx.guild.channels, name=channel)
    #         async for message in channel.history(limit=int(count)):
    #             if arg == 'search everything':
    #                 justdate = str(message.created_at.day) + str(message.created_at.month) + str(message.created_at.year)
    #                 if justdate == previousdate:
    #                     dayusecount = dayusecount + 1
    #                     messagecollectedcount = messagecollectedcount + 1
    #                     if messagecollectedcount % 500 == 0:
    #                         print("Searching... collected {0} messages.".format(messagecollectedcount))
    #                 else:
    #                     timegraph.append(dayusecount)
    #                     dayusecount = 0
    #                     daycount = daycount + 1
    #                     messagecollectedcount = messagecollectedcount + 1
    #                     axis.append(message.created_at)
    #                     if messagecollectedcount % 500 == 0:
    #                         print("Searching... collected {0} messages.".format(messagecollectedcount))
    #                 previousdate = justdate
    #             elif arg in message.content:
    #                 justdate = str(message.created_at.day) + str(message.created_at.month) + str(message.created_at.year)
    #                 if justdate == previousdate:
    #                     dayusecount = dayusecount + 1
    #                     messagecollectedcount = messagecollectedcount + 1
    #                     if messagecollectedcount % 500 == 0:
    #                         print("Searching... collected {0} messages.".format(messagecollectedcount))
    #                 else:
    #                     timegraph.append(dayusecount)
    #                     dayusecount = 0
    #                     daycount = daycount + 1
    #                     messagecollectedcount = messagecollectedcount + 1
    #                     if messagecollectedcount % 500 == 0:
    #                         print("Searching... collected {0} messages.".format(messagecollectedcount))
    #                     axis.append(message.created_at)
    #                 previousdate = justdate
    #         dates = timegraph
    #         plt.plot_date(axis, dates, "g")
    #         #plt.autoscale(enable = True)
    #         plt.gcf().autofmt_xdate()
    #         if serversearch == False:
    #             plt.figtext(0, .90, "Graph of usage for {0} in {1}".format(arg, channel), fontdict = None)
    #         elif serversearch == True:
    #             plt.figtext(0, .90, "Graph of usage for {0} in {1}".format(arg, ctx.guild), fontdict=None)
    #         plt.savefig('graph.png', bbox_inches='tight')
    #         plt.close()
    #         rawgraph = open('graph.png', 'rb')
    #         photo = discord.File(fp=rawgraph, filename="graph.png")
    #         await ctx.send(file = photo)
    #         rawgraph.close()
    #         await searchinprogress.delete()
    #         searching = False
    #     elif searching == True:
    #         await ctx.send("Currently searching, try again later.")
    #
    # @oldsearch.error
    # async def search_error(self, ctx, error):
    #     global searching
    #     if isinstance(error, commands.errors.BadArgument):
    #         await ctx.send("The proper form is !search [channel] [number of posts] [word(s) to search].")
    #         searching = False
    #     elif isinstance(error, commands.errors.MissingRequiredArgument):
    #         await ctx.send("Not enough arguments.")
    #         searching = False
    #     else:
    #         await ctx.send("Could not search; {0}.".format(error))
    #         searching = False
    #
    # @commands.command()
    # async def emojistats (self, ctx, channel, count):
    #     global searching
    #     if not searching:
    #         searching = True
    #         await ctx.send("Gathering data.")
    #
    #         emojiList = await gatherEmojiList(ctx)
    #
    #         channel = discord.utils.get(ctx.guild.channels, name=channel)
    #         async for message in channel.history(limit=int(count)):
    #             if message.reactions == []:
    #                 pass
    #             else:
    #                 for reaction in message.reactions:
    #                     if reaction.custom_emoji:
    #                         for emojiInfo in emojiList:
    #                             if reaction.emoji.name in emojiInfo:
    #                                 emojiInfo[1] += reaction.count
    #                     else:
    #                         pass
    #         # emojiNameList = []
    #         # emojiCountList = []
    #         # for emojiInfo in emojiList:
    #         #     emojiNameList.append(emojiInfo[0])
    #         #     emojiCountList.append(emojiInfo[1])
    #         # for emoji in emojiList:
    #         #     emojiString +="{: >20}".format(*emojiNameList)+ "{: >20}".format( *emojiCountList)
    #         emojiList = sorted(emojiList, key=itemgetter(1))
    #         emojiList.reverse()
    #         emojiString = ""
    #         for emojiInfo in emojiList:
    #             emojiString += await addSpaces(emojiInfo[0])+" "+str(emojiInfo[1])+"\n"
    #         await ctx.send("```"+emojiString+"```")
    #         searching = False
    #     elif searching:
    #         await ctx.send("Currently searching, try again later.")
#
#
# async def addSpaces(string):
#     if len(string) < 30:
#         string += " "*(30-len(string))
#     return string
#
# async def gatherEmojiList(ctx):
#     emojiList = []
#     for emoji in ctx.guild.emojis:
#         emojiList.append([emoji.name, 0])
#     return emojiList
#

async def total_user_stats(ctx, user, index):
    async with ctx.channel.typing():
        pending_search_message = await ctx.send(f"Searching for total user stats on {user.display_name}.")
        message_count = 0
        average_length_list = []
        average_length_sum = 0
        average_length = 1
        for channel in index:
            for message in channel:
                if message.author == user:
                    average_length_list.append(len(message.content))
                    message_count += 1
        for x in average_length_list:
            average_length_sum += x
        try:
            average_length = average_length_sum/len(average_length_list)
        except:
            await ctx.send("ERROR; CANNOT DIVIDE BY ZERO; SOMETHING WENT WRONG.")
    em = discord.Embed(title='User Stats', description=f"Message count:         {message_count}\n"
                                                       f"Average (char) length: {round(average_length, 2)}", colour=0xFFD700)
    em.set_author(name=user.display_name, icon_url=user.avatar_url)
    em.set_footer(text='The data\'s probably accurate...')
    await pending_search_message.delete()
    return em


def check_if_rbnr(ctx):
    return ctx.guild.id == rbnr


def setup(bot):
    bot.add_cog(StatCommands(bot))