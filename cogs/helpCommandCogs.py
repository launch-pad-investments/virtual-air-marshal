"""
COGS: used for help commands
"""

import os
import sys

import discord
from discord.ext import commands
from discord import Permissions, Embed
from cogs.toolsCog.books import GeneralHelp

from utils.jsonReader import Helpers
from cogs.toolsCog.systemMessages import CustomMessages

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)
customMessages = CustomMessages()
menu = GeneralHelp()
helper = Helpers()

bot_setup = helper.read_json_file(file_name='mainBotConfig.json')


class HelpCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot    
    
    @commands.command()
    async def help(self, ctx):
        if ctx.invoked_subcommand is None:
            pass
            
        
    @help.command()
    async def jail(self, ctx):
        pass
    
    @help.command()
    async def spam(self, ctx):
        pass
        
def setup(bot):
    bot.add_cog(HelpCommands(bot))