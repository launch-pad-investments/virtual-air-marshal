import os
import sys

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

from backoffice.spamSystemDb import SpamSystemManager
from backoffice.jailSystemDb import JailSystemManager
from backoffice.supportSystemDb import SupportSystemManager
import discord
from discord import Embed, Colour, Permissions
from discord.ext import commands
from backoffice.jailManagementDb import JailManagement
from utils.jsonReader import Helpers
from backoffice.loggerSystemDb import LoggerSystem
from cogs.toolsCog.systemMessages import CustomMessages
from cogs.toolsCog.checks import is_public, is_jail_not_registered, is_community_owner, is_spam_not_registered, \
    is_overwatch, is_support_not_registered

helper = Helpers()
sup_sys_mng = SupportSystemManager()
spam_sys_mng = SpamSystemManager()
jail_sys_mgn = JailSystemManager()
jail_manager = JailManagement()
logger = LoggerSystem()
custom_message = CustomMessages()
bot_setup = helper.read_json_file(file_name='mainBotConfig.json')


class HelpCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.command = bot_setup['command']

    @commands.command()
    @commands.check(is_public)
    @commands.check_any(commands.check(is_overwatch), commands.check(is_community_owner))
    async def help(self, ctx):
        help_nfo = Embed(title=f'Welcome to virtual air marshall',
                         description='Welcome to help menu. All available command entry points are presented below',
                         colour=Colour.green())
        help_nfo.add_field(name=f'Bot links',
                           value=f'[Web Page](https://launch-pad-investments.github.io/virtual-air-marshal/)\n'
                                 f'[Github](https://github.com/launch-pad-investments/virtual-air-marshal)',
                           inline=False)
        help_nfo.add_field(name=f'Administrative section',
                           value=f'```{self.command}admin```',
                           inline=False)
        help_nfo.add_field(name=f'Service registration area',
                           value=f'```{self.command}services```',
                           inline=False)
        help_nfo.add_field(name=f'Logger handler commands',
                           value=f'```{self.command}logger```',
                           inline=False)
        help_nfo.add_field(name=f'Spam protection handler commands',
                           value=f'```{self.command}spam```',
                           inline=False)
        await ctx.channel.send(embed=help_nfo)

    @help.error
    async def h_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            msg = f"In order for you to be able to access this area please use one of the public channels of the " \
                  f"server where bot has access to"
            await ctx.channel.send(content=msg)
        elif isinstance(error, commands.CheckAnyFailure):
            msg = "You are allowed to access this command only if you are the owner of the community or part of the" \
                  " Virtual Air Marshal dev team"
            await ctx.channel.send(content=msg)


def setup(bot):
    bot.add_cog(HelpCommands(bot))
