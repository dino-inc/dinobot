import discord
from discord.ext import commands


class Adventure:
    def __init__(self, bot):
        self.bot = bot
        self.fightState = False
        self.menuContainer = MenuContainer()


    @commands.command(help="Begin a fight.")
    async def fight(self, ctx):
        if not self.fightState:
            self.fightState = True
            fightMessage = await ctx.send('Began the fight!')
            #fight_game(ctx, fighter, fightMessage, self.fightState)
        else:
            await ctx.send('A fight is already in progress.')

    # @commands.command(help = "Ends a fight.")
    # async def surrender(self, ctx):
    #     if self.fightState == True:
    #         self.fightState = False
    #         await ctx.send('Ended the fight.')
    #     else:
    #         await ctx.send('There is no fight to end.')

    @commands.command(help="test of interactive buttons")
    async def buttontest(self, ctx):

        testMenu = Menu(ctx, "Testing a new menu class.", ctx.author)
        await self.menuContainer.add_menu(testMenu)
        await testMenu.add_button('sword', 'you have clicked shiny swords')
        await testMenu.add_button('smile', 'you have clicked a smiley face')
        await testMenu.send_menu()
        await testMenu.generate_buttons()
    async def on_reaction_add(self, reaction, member):
        await self.menuContainer.process_button_press(reaction, member, self.bot)

class MenuContainer:
    def __init__(self):
        self.menuList = []


    async def add_menu(self, menu):
        self.menuList.append(menu)

    async def process_button_press(self, button_input, member, bot):
        for menu in self.menuList:
            await menu.process_button(button_input, member, bot)


class Menu:
    def __init__(self, ctx, menuText, menuUser):
        self.menuText = menuText
        self.menuUser = menuUser
        self.menuMessage = None
        self.ctx = ctx
        self.buttonList = []

    async def set_text(self, text):
        self.menuText = text

    async def edit_menu_message(self):
        await self.menuMessage.edit(content=self.menuText)

    async def add_button(self, name, text):
        button = Button(name, text)
        self.buttonList.append(button)

    async def generate_buttons(self):
        await self.menuMessage.clear_reactions()
        for button in self.buttonList:
            await button.generate(self.menuMessage)

    async def send_menu(self):
        self.menuMessage = await self.ctx.send(self.menuText)

    async def process_button(self, button_input, member, bot):
        if member == bot.user:
            return
        if button_input.message.id == self.menuMessage.id:
            if member == self.menuUser:
                for button in self.buttonList:
                    if await button.match(button_input):
                        await self.set_text(await button.get_text())
                        await self.edit_menu_message()
                        await self.generate_buttons()
            else:
                await self.menuMessage.remove_reaction(button_input.emoji, member)


class Button:
    def __init__(self, name, text):
        self.buttonEmoji = ['⚔', '😃']
        self.buttonNames = ['sword', 'smile']
        self.buttonText = text
        self.buttonIndex = self.buttonNames.index(name)

    async def set_emoji(self, name):
        self.buttonIndex = self.buttonNames.index(name)

    async def generate(self, menuMessage):
        await menuMessage.add_reaction(self.buttonEmoji[self.buttonIndex])

    async def set_text(self, text):
        self.buttonText = text

    async def get_text(self):
        return self.buttonText

    async def match(self, reaction):
        if reaction.emoji == self.buttonEmoji[self.buttonIndex]:
            return True
        else:
            return False


def setup(bot):
    bot.add_cog(Adventure(bot))