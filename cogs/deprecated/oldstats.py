import discord
from discord.ext import commands
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import relationship, backref
from sqlalchemy import exc
from sqlalchemy import asc
import asyncio
import os
import matplotlib
import numpy as np
from matplotlib import dates
import matplotlib.ticker as tick
import matplotlib.pyplot as pyplot
import operator
import time
from progress.bar import IncrementalBar



# sqlalchemy boilerplate
Base = declarative_base()
engine = create_engine('sqlite:///serverlogs.db')


# Messages within a channel
class Messagedb(Base):
    __tablename__ = "message"
    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, ForeignKey("channel.id"), primary_key=True)
    server_id = Column(Integer, ForeignKey("serverlist.id"))
    content = Column(String)
    bot = Column(Boolean)
    has_embed = Column(Boolean)
    is_pinned = Column(Boolean)
    date = Column(DateTime(timezone=True))
    edited = Column(DateTime(timezone=True))
    reactions = relationship("Reactiondb", lazy="dynamic", backref="message")
    attachments = relationship("Attachmentdb", lazy="dynamic", backref="message")
    author = relationship("Memberdb", lazy="dynamic", secondary="member_message")


# Channel within a server
class Channeldb(Base):
    __tablename__ = "channel"
    topic = Column(String)
    name = Column(String)
    id = Column(Integer, primary_key=True)
    server_id = Column(Integer, ForeignKey("serverlist.id"))
    creation_date = Column(DateTime(timezone=True))
    messages = relationship("Messagedb", lazy="dynamic", backref="channel")


# Servers with the bot
class ServerListdb(Base):
    __tablename__ = "serverlist"
    id = Column(Integer, primary_key=True)
    member_count = Column(Integer)
    creation_date = Column(DateTime(timezone=True))
    channels = relationship("Channeldb", lazy="dynamic", backref="serverlist")
    messages = relationship("Messagedb", lazy="dynamic", backref="server")


# Members with messages
class Memberdb(Base):
    __tablename__ = "member"
    id = Column(Integer, primary_key=True)
    join_date = Column(DateTime(timezone=True))
    creation_date = Column(DateTime(timezone=True))
    messages = relationship("Messagedb", lazy="dynamic", secondary="member_message")


# Junction between members and messages
class Member_Message(Base):
    __tablename__ = "member_message"
    member_id = Column(Integer, ForeignKey("member.id"), primary_key=True)
    message_id = Column(Integer, ForeignKey("message.id"), primary_key=True)


# Store attachments of a message - not used because it really doesn't matter
class Attachmentdb(Base):
    __tablename__ = "attachment"
    message_id = Column(Integer, ForeignKey("message.id"))
    id = Column(Integer, primary_key=True)
    url = Column(String)
    filename = Column(String)


# Store reactions of a message
class Reactiondb(Base):
    __tablename__ = "reaction"
    reaction_index = Column('index', Integer, index=True, primary_key=True)
    message_id = Column(Integer, ForeignKey("message.id"))
    emoji_name = Column(String, unique=False)
    emoji_id = Column(String)
    count = Column(Integer)
    is_custom_emoji = Column(Boolean)


Base.metadata.create_all(engine)


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.Session = sessionmaker(bind=engine)
        # Samsara, then personal testing server
        self.log_servers = [231084230808043522]

    # Add new messages to database as they arrive
    @commands.Cog.listener()
    async def on_message(self, message):
        # Disable logging for servers I'm not actively logging because there's no need for logging there
        if message.guild.id not in self.log_servers:
            return
        session = self.Session()
        await validate_serverdb(session, message.guild)
        channeldb = get_channeldb(session, message.guild, message.channel)
        await create_message(session, channeldb, message)
        session.commit()
        session.close()

    # The primary logging command
    @commands.command()
    async def log_server(self, ctx):
        if (ctx.author.id != 141695444995670017):
            return
        await ctx.send(f"Logging {ctx.guild.name}.")
        session = self.Session()
        await validate_serverdb(session, ctx.guild)
        logged_channels = "Logged channels:\n"
        for channel in ctx.guild.text_channels:
            logged_channels += await log_channel(session, ctx, channel)
            logged_channels = await split_string(ctx, logged_channels)
        session.commit()
        session.close()
        await ctx.send(logged_channels+"Logging completed.\n")


    @commands.command()
    async def log_channel(self, ctx, channel: discord.TextChannel):
        if (ctx.author.id != 141695444995670017):
            return
        await ctx.send(f"Logging {channel.name}.")
        session = self.Session()
        await validate_serverdb(session, ctx.guild)
        logged_channels = "Logged channels:\n"
        logged_channels += await log_channel(session, ctx, channel)
        session.commit()
        session.close()
        await ctx.send(logged_channels+"Logging completed.\n")

    @commands.is_owner()
    @commands.command()
    async def show(self, ctx, count: int):
        session = self.Session()
        query = session.query(ServerListdb).filter_by(id=ctx.guild.id).first().channels.filter_by(id=ctx.channel.id)\
                .first().messages.all()
        composite_msg = f"The first {count} messages are:\n"
        for dbmessage in query:
            composite_msg += f"{dbmessage.content}\n"
            count -= 1
            if count == 0:
                break
        await ctx.send(composite_msg)
        session.close()

    @commands.is_owner()
    @commands.command()
    async def show_channels(self, ctx):
        session = self.Session()
        query = session.query(ServerListdb).filter_by(id=ctx.guild.id).first()
        if query is None:
            await ctx.send("There are no logged channels.")
        else:
            query = query.channels.all()
            composite_msg = f"The logged channels of the server are:\n"
            for channel in query:
                composite_msg += f"{channel.name}\n"
            await ctx.send(composite_msg)

    @commands.is_owner()
    @commands.command()
    async def howmany(self, ctx, member: discord.Member):
        session = self.Session()
        await ctx.send(f"{member.display_name} ({member.name}) has sent "
                       f"{len(get_member_messages(session, ctx, member.id))} messages in {ctx.guild.name}.")
        session.close()


    @commands.is_owner()
    @commands.command()
    async def cleardb(self, ctx):
        def verify_user(message):
            if message.author == ctx.message.author and message.channel == ctx.message.channel:
                return True
            else:
                return False
        await ctx.send("Are you sure you want to delete the database? Type \"DELETE\" to delete.")
        choice = ""
        try:
            choice = await self.bot.wait_for('message', check=verify_user, timeout=30)
        except asyncio.TimeoutError:
            await ctx.send(f"No input found, exiting command.")
            session.close()
            return
        if choice.content == "DELETE":
            delete_db(Base)
            await ctx.send(f"Database is now deleted.")
        else:
            await ctx.send("Could not confirm, exiting command.")

    @commands.group(name="graph")
    async def graph(self, ctx):
        pass

    @graph.command()
    async def total_msg(self, ctx, channel : discord.TextChannel):
        await ctx.send("Generating graph of total messages over time.")
        session = self.Session()
        await validate_serverdb(session, ctx.guild)
        # Sort all messages by date
        #messages = session.query(ServerListdb).filter_by(id=ctx.guild.id).first().messages.order_by(asc(Messagedb.date)).all()
        # Instead, do it all for a specific channel
        messages = session.query(Channeldb).filter_by(id=channel.id).first().messages.filter_by(channel_id=channel.id).order_by(asc(Messagedb.date))

        datearray = []
        accumulated_messages = 0
        accumulated_messages_array = []
        previous_date = 0
        for message in messages:
            # currentdate = str(message.date.day) + str(message.date.month) + str(message.date.year)
            currentdate = str(message.date.month) + str(message.date.year)
            if currentdate == previous_date:
                accumulated_messages += 1
            else:
                previous_date = currentdate
                datearray.append(dates.date2num(message.date))
                accumulated_messages_array.append(accumulated_messages)
                accumulated_messages = 0
        #ax.plot_date(datearray, accumulated_messages_array, 'b-', linestyle='solid', xdate=True, ydate=False)
        session.close()

        # Graph generation!
        fig = pyplot.figure()
        fig.patch.set_alpha(1)
        fig.patch.set_facecolor('#DEB887')
        fig.tight_layout()

        ax = fig.add_subplot(1,1,1)
        ax.plot_date(datearray, accumulated_messages_array, 'r-', linestyle='solid', xdate=True, ydate=False)

        ax.set_facecolor('#FFFDD0')
        pyplot.grid(True, color = 'lightcoral')

        pyplot.xticks(rotation=30)
        pyplot.xlabel("date")
        pyplot.ylabel("messages")
        pyplot.title(f"Total messages in {channel.name} per month")
        pyplot.savefig("graph.png", facecolor=fig.get_facecolor())
        raw_graph = open('graph.png', 'rb')
        photo = discord.File(fp=raw_graph, filename="graph.png")
        await ctx.send(file=photo)
        raw_graph.close()

    @commands.is_owner()
    @graph.command()
    async def user_vs_total(self, ctx, member: discord.Member):
        await ctx.send("Generating graph of total messages over time with a user.")
        session = self.Session()
        await validate_serverdb(session, ctx.guild)
        # Sort all messages by date
        messages = session.query(ServerListdb).filter_by(id=ctx.guild.id).first().messages.order_by(asc(Messagedb.date)).all()

        datearray = []
        total_messages = 0
        current_messages = []
        for message in messages:
            datearray.append(dates.date2num(message.date))
            total_messages += 1
            current_messages.append(total_messages)

        messages = session.query(Memberdb).filter_by(id=member.id).first().messages.order_by(asc(Messagedb.date)).all()
        memberdatearray = []
        member_total_messages = 0
        member_current_messages = []
        for message in messages:
            memberdatearray.append(dates.date2num(message.date))
            member_total_messages += 1
            member_current_messages.append(member_total_messages)
        session.close()

        # Graph generation!
        fig = pyplot.figure()
        fig.patch.set_alpha(1)
        fig.patch.set_facecolor('#DEB887')
        fig.tight_layout()

        ax = fig.add_subplot(1,1,1)
        ax.plot_date(memberdatearray, member_current_messages, 'b-', linestyle='solid', xdate=True, ydate=False)
        ax.plot_date(datearray, current_messages, 'r-', linestyle='solid', xdate=True, ydate=False)

        ax.set_facecolor('#FFFDD0')
        pyplot.grid(True, color = 'lightcoral')

        pyplot.xticks(rotation=30)
        pyplot.xlabel("date")
        pyplot.ylabel("messages")
        pyplot.title(f"Total messages in {ctx.guild.name} over time with {member.display_name}'s messages")
        pyplot.savefig("graph.png", facecolor=fig.get_facecolor())
        raw_graph = open('graph.png', 'rb')
        photo = discord.File(fp=raw_graph, filename="graph.png")
        await ctx.send(file=photo)
        raw_graph.close()

    @graph.command()
    async def messages_per(self, ctx, length, total_server: bool, member : discord.Member):
        print(f"Graphing request by {ctx.author.display_name}")
        if(total_server == True and ctx.author.id != 141695444995670017):
            await ctx.send("Please do not use this unless you are dino.")
            return
        if length != "day" and length != "month":
            await ctx.send("Invalid length parameter.")
            return
        await ctx.send(f"Generating graph of messages per {length}.")

        # Graph generation!
        fig = pyplot.figure(num=None, figsize=(16, 6), dpi=100)
        fig.patch.set_alpha(1)
        fig.patch.set_facecolor('#DEB887')
        fig.tight_layout()
        ax = fig.add_subplot(1, 1, 1)

        session = self.Session()
        await validate_serverdb(session, ctx.guild)
        if total_server:
            # Sort all messages by date
            message_query = session.query(ServerListdb).filter_by(id=ctx.guild.id).first().messages\
                            .order_by(asc(Messagedb.date)).all()
            datearray = []
            accumulated_messages = 0
            accumulated_messages_array = []
            previous_date = 0
            for message in message_query:
                currentdate = 0
                if length == "day":
                    currentdate = str(message.date.day) + str(message.date.month) + str(message.date.year)
                elif length == "month":
                    currentdate = str(message.date.month) + str(message.date.year)
                if currentdate == previous_date:
                    accumulated_messages += 1
                else:
                    previous_date = currentdate
                    datearray.append(dates.date2num(message.date))
                    accumulated_messages_array.append(accumulated_messages)
                    accumulated_messages = 0
            ax.plot_date(datearray, accumulated_messages_array, 'r-', linestyle='solid', xdate=True, ydate=False)

        message_query = session.query(Memberdb).filter_by(id=member.id).first().messages.filter_by(server_id=ctx.guild.id).order_by(asc(Messagedb.date)).all()
        datearray = []
        accumulated_messages = 0
        accumulated_messages_array = []
        previous_date = 0
        for message in message_query:
            currentdate = 0
            if length == "day":
                currentdate = str(message.date.day) + str(message.date.month) + str(message.date.year)
            elif length == "month":
                currentdate = str(message.date.month) + str(message.date.year)
            if currentdate == previous_date:
                accumulated_messages += 1
            else:
                previous_date = currentdate
                datearray.append(dates.date2num(message.date))
                accumulated_messages_array.append(accumulated_messages)
                accumulated_messages = 0
        ax.plot_date(datearray, accumulated_messages_array, 'b-', linestyle='solid', xdate=True, ydate=False)
        session.close()


        ax.set_facecolor('#FFFDD0')
        pyplot.grid(True, color = 'lightcoral')

        pyplot.xticks(rotation=30)
        pyplot.xlabel("date")
        pyplot.ylabel("messages")
        pyplot.title(f"Messages per {length} in {ctx.guild.name} of {member.name}.")
        pyplot.tight_layout()
        pyplot.savefig("graph.png", facecolor=fig.get_facecolor())
        raw_graph = open('graph.png', 'rb')
        photo = discord.File(fp=raw_graph, filename="graph.png")
        await ctx.send(file=photo)
        raw_graph.close()

    @graph.command()
    async def channel_pie(self, ctx, channel: discord.TextChannel):
        if (ctx.author.id != 141695444995670017):
            return
        await ctx.send("Generating graph of channel message distribution.")
        # Graph generation!
        fig = pyplot.figure(num=None, figsize=(16, 6), dpi=100)
        fig.patch.set_alpha(1)
        fig.patch.set_facecolor('#DEB887')
        fig.tight_layout()
        ax = fig.add_subplot(1, 1, 1)
        session = self.Session()
        await validate_serverdb(session, ctx.guild)
        message_query = session.query(Channeldb).filter_by(id=channel.id).first().messages.filter_by(
            channel_id=channel.id).order_by(asc(Messagedb.date))
        member_stat_dict = {}
        print("Beginning message analysis.")
        bar = IncrementalBar("Processing", max=message_query.count(),
                             suffix=f"Elapsed: %(elapsed)ds - %(percent).1f%% - %(remaining)d left - %(eta)ds remaining")
        bar.check_tty = False
        start = time.perf_counter()
        for message in message_query:
            member_id = message.author.first().id
            member_name = discord.utils.get(ctx.guild.members, id=member_id)
            if member_name is None:
                continue
            if member_stat_dict.get(member_name) is None:
                member_stat_dict[member_name] = 1
            else:
                member_stat_dict[member_name] = member_stat_dict[member_name] + 1
            bar.next()
        end = time.perf_counter()
        print(f"\nMessage analysis finished in {end-start:0.4f} seconds.")
        sorted_dict = sorted(member_stat_dict.items(), key=operator.itemgetter(1))
        names, count = zip(*sorted_dict)
        fig1, ax = pyplot.subplots()
        ax.set_facecolor('#FFFDD0')
        ax.pie(count, labels=names, autopct='%1.1f%%',
                shadow=True, startangle=90, rotatelabels=True)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        pyplot.savefig("graph.png", facecolor=fig.get_facecolor())

        raw_graph = open('graph.png', 'rb')
        photo = discord.File(fp=raw_graph, filename="graph.png")
        await ctx.send(file=photo)
        raw_graph.close()


# Gets the messages from a user on the guild the ctx is from
def get_member_messages(session, ctx, member_id):
    message_query = session.query(Memberdb).filter_by(id=member_id).first().messages
    message_list = []
    for message in message_query:
        if message.channel.serverlist.id == ctx.guild.id:
            message_list.append(message)
    return message_list


# Gets the channeldb object from a channel object
def get_channeldb(session, guild, channel):
    serverdb = session.query(ServerListdb).filter_by(id=guild.id).first()
    channeldb = serverdb.channels.filter_by(id=channel.id).first()
    if channeldb is None:
        print(f"Creating entry for channel {channel.name}.")
        channeldb = Channeldb(id=channel.id, name=channel.name, creation_date=channel.created_at)
        serverdb.channels.append(channeldb)
        session.commit()
    return channeldb


# Create server if it doesn't exist
async def validate_serverdb(session, guild):
    serverdb = session.query(ServerListdb).filter_by(id=guild.id).first()
    if serverdb is None:
        serverdb = ServerListdb(id=guild.id, member_count=guild.member_count,
                                creation_date=guild.created_at)
        session.add(serverdb)
        session.commit()
        print(f"Creating entry for server {guild.name}.")


async def log_channel(session, ctx, channel):
    print(f"Logging {channel.name}.")
    # Get the channel whose ID matches the message... if it exists
    channeldb = get_channeldb(session, channel.guild, channel)
    # Overly broad try except, go!
    try:
        new_msg_counter = 0
        skip_msg_counter = 0
        async for msg in channel.history(limit=None, oldest_first=True):
            print(f"Logged {new_msg_counter} and skipped {skip_msg_counter}.")
            # Get the message whose ID matches the message... if it exists
            msg_db = channeldb.messages.filter_by(id=msg.id).first()
            # Check if there is no message whose ID matches the iterated message
            if msg_db is None:
                # Keep track of how many new messages are created
                new_msg_counter += 1
                # Create the message
                await create_message(session, channeldb, msg)
            else:
                skip_msg_counter += 1
                continue
        session.commit()
        logged_channels = f"Logged {new_msg_counter} messages (Skipped {skip_msg_counter}) from <#{channel.id}>.\n"
        return logged_channels

    except Exception as e:
        logged_channels = f"Skipping <#{channel.id}> for {e}.\n"
        return logged_channels


async def split_string(ctx, string):
    if len(string) > 1800:
        await ctx.send(string)
        string = ""
        return string
    else:
        return string



async def create_message(session, channeldb, msg):
    # Creates a new member category if necessary
    # Queries for author ID
    authorquery = session.query(Memberdb).filter_by(id=msg.author.id).first()
    # If the member is not found, create it
    if authorquery is None:
        author = Memberdb(id=msg.author.id, creation_date=msg.author.created_at)
        # There's two types of users, because of course there is
        if type(msg.author) is discord.User:
            setattr(author, "join_date", None)
        else:
            setattr(author, "join_date", msg.author.joined_at)
        session.add(author)
        session.commit()

    msg_db = Messagedb(id=msg.id, content=msg.content, bot=False, has_embed=False, is_pinned=False,
                       date=msg.created_at, edited=msg.edited_at)
    authorquery = session.query(Memberdb).filter_by(id=msg.author.id).first()
    msg_db.author.append(authorquery)
    # Set the bot value
    if msg.author.bot:
        setattr(msg_db, "bot", True)
    # Sets if it has an embed
    if msg.embeds is not None:
        setattr(msg_db, "has_embeds", True)
    # Sets if it is pinned
    if msg.pinned:
        setattr(msg_db, "pinned", True)
    # Logs reactions
    for reaction in msg.reactions:
        # Handles the string case of emojis
        if type(reaction.emoji) is str:
            reactiondb = Reactiondb(emoji_name=reaction.emoji, emoji_id=None, count=reaction.count)
        # Handles partial emojis
        elif type(reaction.emoji) is discord.partial_emoji.PartialEmoji:
            reactiondb = Reactiondb(emoji_name=reaction.emoji.name, emoji_id=reaction.emoji.id,
                                    count=reaction.count)
            if reaction.emoji.is_custom_emoji():
                setattr(reactiondb, "is_custom_emoji", True)
        # Handles the only good emojis
        else:
            reactiondb = Reactiondb(emoji_name=reaction.emoji.name, emoji_id=reaction.emoji.id,
                                    count=reaction.count)
        msg_db.reactions.append(reactiondb)
    channeldb.messages.append(msg_db)
    channeldb.serverlist.messages.append(msg_db)
    session.commit()


# Deletes the database
def delete_db(Base):
    os.remove("serverlogs.db")
    Base.metadata.create_all(engine)


def setup(bot):
    bot.add_cog(Stats(bot))
