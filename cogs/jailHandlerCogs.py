import os
import sys

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

from datetime import datetime
from datetime import timedelta
import time
from backoffice.spamSystemDb import SpamSystemManager
import discord
from discord import Member as DiscordMember
from discord.ext import commands
from discord.ext.commands import Greedy
from jailList import JailManagement
from utils.jsonReader import Helpers
from cogs.toolsCog.systemMessages import CustomMessages
from colorama import Fore

helper = Helpers()
community_manager = SpamSystemManager()
jail_manager = JailManagement()
customMessages = CustomMessages()
bot_setup = helper.read_json_file(file_name='mainBotConfig.json')

def is_community_registered(ctx):
    return community_manager.check_community_reg_status(community_id=ctx.message.guild.id)

def is_community_not_registered(ctx):
    return community_manager.check_if_not_registered(community_id=ctx.message.guild.id)

def is_public(ctx):
    return ctx.message.channel.type != discord.ChannelType.private

def is_overwatch(ctx):
    access_list = bot_setup['userAccess']
    return [user for user in access_list if ctx.message.author.id == int(user)]

def is_community_owner(ctx):
    return ctx.message.author.id == ctx.message.guild.owner_id

class JailService(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.group()
    @commands.check_any(commands.check(is_overwatch), commands.check(is_community_owner), commands.check(is_community_registered))
    async def jail(self, ctx):
        if ctx.invoked_subcommand is None:
            title = '__Available commands under ***Jail*** category!'
            description = 'Jail system was designed with intentions to keep the language of the community clean and social. If member breaches language for 3 minutes, he/she is sent to jail for 2 minutes.' 
            ' All roles are removed and given back once jail-time has expired.'
            value = [{'name': f'{bot_setup["command"]}jail set <>',
                      'value': "Auto language moderation category of settings for community with auto jail and release function"},
                     ]

            await customMessages.embed_builder(ctx=ctx, title=title, description=description, data=value)
            
            
    # Turn on and turn off
    @jail.command()
    async def on (self,ctx):
        pass
    
    @jail.command()
    async def off (self,ctx):
        pass
    
            
def setup(bot):
    bot.add_cog(JailService(bot))
