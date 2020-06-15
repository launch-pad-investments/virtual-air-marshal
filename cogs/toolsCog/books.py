from discord.ext import menus
from discord import Embed, Colour

class GeneralHelp(menus.Menu):
    async def send_initial_message(self, ctx, channel):
        help_embed = Embed(title='__Air Marshal Manual__',
                           colour=Colour.green())
        help_embed.add_field(name='How to use:',
                             value='Welcome to ')
        return await channel.send(embed=help_embed)

    @menus.button('\N{BLACK RIGHT-POINTING TRIANGLE}\ufe0f')
    async def go_to_next_page(self, payload):
        pass
        
        
    @menus.button('\N{BLACK SQUARE FOR STOP}\ufe0f')
    async def on_stop(self, payload):
        self.stop()
        

        

class JailGeneralMenu(menus.Menu):
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