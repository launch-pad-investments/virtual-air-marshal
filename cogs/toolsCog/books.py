from discord.ext import menus
from discord import Embed, Colour
from utils.jsonReader import Helpers

helper = Helpers()
bot_setup = helper.read_json_file(file_name='mainBotConfig.json')

class GeneralHelp(menus.Menu):
    async def send_initial_message(self, ctx, channel):
        help_embed = Embed(title='__Air Marshal Help__',
                           colour=Colour.green())
        help_embed.add_field(name='How to use:',
                             value='Welcome to the interractive help. Please use arrows to navigate through the book.')
        return await channel.send(embed=help_embed)

    @menus.button('\N{BLACK RIGHT-POINTING TRIANGLE}\ufe0f')
    async def go_to_next_page(self, payload):
        jail_embed = Embed(title='__Jail Service and Profanity protection system__',
                           description='This is automatic service which monitors guild for use of bad language and automatically punishes users.',
                           colour=Colour.green())
        jail_embed.add_field(name="How does it work?",
                             value="When turned ON, system automatically monitors all channels, of the community where bot has access to, for bad words."
                             " Once bad word is identified, it marks the strike in database for particular user, deletes the message, and notifies user",
                             inline=False)
        jail_embed.add_field(name="Laws and sentece",
                        value="Once user breaches the rules 3 times, it will be automatically given the role Jailed, where rights for positng will be removed."
                        " Rights for the Jailed role can be modified by guild administrators and owner in order to suit the needs of the community. Additionally, "
                        " bot will store the users pre-jail state of perks and roles, remove them, and returned them back once sentence time is served.",
                        inline=False)
        jail_embed.add_field(name="Sentece duration",
                        value="Currently bot is pre-set to issue a 5 minute jail time to the user who has filled 3 strikes.",
                        inline=False)
        jail_embed.add_field(name="How to set up?",
                        value=f"You need to be either administrator or owner of the communtiy to create service. Follows the steps presented bellow:\n"
                        f"***1-> {bot_setup['command']}service register jail*** (bot will automatically create all necessary roles)\n"
                        f"***2-> {bot_setup['command']}jail on *** (Turn the jail service on)",
                        inline=False)
        await self.message.edit(embed=jail_embed)
                
    @menus.button('\N{BLACK SQUARE FOR STOP}\ufe0f')
    async def on_stop(self, payload):
        await self.message.delete()
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