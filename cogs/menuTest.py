from discord.ext import menus
from discord import Embed, Colour
        
class HelpGeneralMenu(menus.Menu):
    async def send_initial_message(self, ctx, channel):
        help_embed = Embed(title='__Air Marshal Manual__',
                           description='Navigate through pages with the help of emojis',
                           colour=Colour.green())
        help_embed.add_field(name='Welcome',
                             value='woot')
        return await channel.send(embed=help_embed)

    @menus.button('\N{THUMBS UP SIGN}')
    async def on_thumbs_up(self, payload):
        await self.message.edit(content=f'Thanks {self.ctx.author}!')

    @menus.button('\N{THUMBS DOWN SIGN}')
    async def on_thumbs_down(self, payload):
        await self.message.edit(content=f"That's not nice {self.ctx.author}...")

    @menus.button('\N{BLACK SQUARE FOR STOP}\ufe0f')
    async def on_stop(self, payload):
        self.stop()
        
    @menus.button('\N{BLACK LEFT-POINTING TRIANGLE}\ufe0f')
    async def on_reset(self,payload):
        await self.message.edit(content=f"Resetting {self.ctx.author}...")
        
        
class Confirm(menus.Menu):
    def __init__(self, msg):
        super().__init__(timeout=30.0, delete_message_after=True)
        self.msg = msg
        self.result = None

    async def send_initial_message(self, ctx, channel):
        return await channel.send(self.msg)

    @menus.button('\N{WHITE HEAVY CHECK MARK}')
    async def do_confirm(self, payload):
        self.result = True
        self.stop()

    @menus.button('\N{CROSS MARK}')
    async def do_deny(self, payload):
        self.result = False
        self.stop()

    async def prompt(self, ctx):
        await self.start(ctx, wait=True)
        return self.result