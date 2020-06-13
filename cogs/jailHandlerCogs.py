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
from cogs.toolsCog.checks import is_community_owner, is_overwatch, is_community_registered

helper = Helpers()
jail_sys_manager = JailSystemManager()
jail_manager = JailManagement()

custom_message = CustomMessages()
bot_setup = helper.read_json_file(file_name='mainBotConfig.json')


class JailService(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.group()
    @commands.check_any(commands.has_guild_permissions(administrator=True),commands.check(is_overwatch), commands.check(is_community_owner), commands.check(is_community_registered))
    async def jail(self, ctx):
        if ctx.invoked_subcommand is None:
            title = '__Available commands under ***Jail*** category!'
            description = 'Jail system was designed with intentions to keep the language of the community clean and social. If member breaches language for 3 minutes, he/she is sent to jail for 2 minutes.' 
            ' All roles are removed and given back once jail-time has expired.'
            value = [{'name': f'{bot_setup["command"]}jail on',
                      'value': "Turns the jail ON"},
                     {'name': f'{bot_setup["command"]}jail off',
                      'value': "Turns the jail system off"}
                     ]

            await custom_message.embed_builder(ctx=ctx, title=title, description=description, data=value)
            
    @jail.command()
    @commands.check(is_community_registered)
    async def on(self,ctx):
        try:
            await ctx.message.delete()
        except Exception:
            pass

        if jail_sys_manager.turn_on_off(community_id=int(ctx.message.guild.id),direction=1):
            title='__System Message__'
            message = 'You have turned ON the automatic jail system and profanity monitor successfully. '
            await custom_message.system_message(ctx=ctx, color_code=0, message = message, destination = 1, sys_msg_title=title)
        else:
            message = f'There was a backend error. Please try again later or contact one of the administrators on the community. We apologize for inconvinience'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
    
    @jail.command() 
    @commands.check(is_community_registered)
    async def off(self,ctx):
        try:
            await ctx.message.delete()
        except Exception:
            pass
        
        if jail_sys_manager.turn_on_off(community_id=int(ctx.message.guild.id),direction=0):
                title='__System Message__'
                message = 'You have turned OFF automtic jail system and profanity successfully. Your members can get crazy'
                await custom_message.system_message(ctx=ctx, color_code=0, message = message, destination = 1, sys_msg_title=title)
        else:
            message = f'There was a backend error. Please try again later or contact one of the administrators on the community. We apologize for inconvinience'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)

    @jail.command()
    async def release (self, ctx, user:DiscordMember):
        # Check if member in jail
        # Remove member from jail 
        # Return roles to member
        print('release')
        pass
    
    @jail.command()
    async def punish(self, ctx, user:DiscordMember, duration:int):
        # Jail members
        print('Punish')
        pass
        
def setup(bot):
    bot.add_cog(JailService(bot))
