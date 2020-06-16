import os
import sys

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

from datetime import datetime
from datetime import timedelta
import time
import discord
from discord import Member as DiscordMember

from backoffice.jailSystemDb import JailSystemManager
from backoffice.jailManagementDb import JailManagement

from discord.ext import commands
from discord.ext.commands import Greedy
from utils.jsonReader import Helpers
from cogs.toolsCog.systemMessages import CustomMessages
from colorama import Fore
from cogs.toolsCog.checks import is_community_owner, is_overwatch, is_community_registered, is_public

helper = Helpers()
jail_sys_manager = JailSystemManager()
jail_manager = JailManagement()

custom_message = CustomMessages()
bot_setup = helper.read_json_file(file_name='mainBotConfig.json')


class SupportService(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.group()
    @commands.check(is_public)
    @commands.bot_has_guild_permissions(administrator=True, manage_messages=True, manage_roles=True)
    @commands.check_any(commands.has_guild_permissions(administrator=True),commands.check(is_overwatch), commands.check(is_community_owner))
    async def jail(self, ctx):
        if ctx.invoked_subcommand is None:
            title = '__Available commands under ***Jail*** category!__'
            description = 'Jail system was designed with intentions to keep the language of the community clean and social. If member breaches language for 3 minutes, he/she is sent to jail for 2 minutes.' 
            ' All roles are removed and given back once jail-time has expired.'
            value = [{'name': f'{bot_setup["command"]}jail on',
                      'value': "Turns the jail ON"},
                     ]

            await custom_message.embed_builder(ctx=ctx, title=title, description=description, data=value)
                
def setup(bot):
    bot.add_cog(JailService(bot))
