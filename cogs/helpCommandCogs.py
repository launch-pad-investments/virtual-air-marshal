import os
import sys

import discord
from discord.ext import commands
from discord import Permissions, Colour
from git import Repo, InvalidGitRepositoryError
from cogs.menuTest import HelpGeneralMenu

from utils.jsonReader import Helpers
from cogs.toolsCog.systemMessages import CustomMessages
from cogs.toolsCog.checks import is_overwatch

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)
customMessages = CustomMessages()
menu = HelpGeneralMenu()
helper = Helpers()

bot_setup = helper.read_json_file(file_name='mainBotConfig.json')


class HelpCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot    
    
    @commands.command()
    async def help(self,ctx):
        await menu.start(ctx)
        
def setup(bot):
    bot.add_cog(HelpCommands(bot))