from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from chatterbot.trainers import ListTrainer
import discord
from discord.ext import commands

chatterbot = ChatBot('dino', filters=["chatterbot.filters.RepetitiveResponseFilter"])
class ChatBot:
    def __init__(self, bot):
        self.bot = bot



    @commands.command(help="Experimental chatbot.")
    async def chatbot(self, ctx, *, input):
        self.bot.loop.create_task(process_command(ctx, input))

    @commands.command()
    @commands.is_owner()
    async def train(self, ctx, count, channel):
        print('Beginning training.')
        trainingList = []
        chatterbot.set_trainer(ChatterBotCorpusTrainer)
        chatterbot.train("chatterbot.corpus.english")
        chatterbot.set_trainer(ListTrainer)
        print('Finished basic english.')
        channel = discord.utils.get(ctx.guild.channels, name=channel)
        async for x in channel.history(limit=int(count), ):
            trainingList.append(x.content)
        trainingList.reverse()
        print('Created training list.')
        chatterbot.train(trainingList)
        print("Finished training.")

async def process_command(ctx, input):
    print("Processing message: " + input)
    response = chatterbot.get_response(input)
    print("Sending message: " + str(response))
    await ctx.send(response)


def setup(self):
    self.add_cog(ChatBot(self))