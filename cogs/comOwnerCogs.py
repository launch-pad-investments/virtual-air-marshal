import os
import sys

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

from datetime import datetime
from datetime import timedelta
import time
from backoffice.spamSystemDb import SpamSystemManager
from backoffice.jailSystemDb import JailSystemManager
import discord
from discord import Member as DiscordMember
from discord.ext import commands
from discord.ext.commands import Greedy
from jailList import JailManagement
from utils.jsonReader import Helpers
from cogs.toolsCog.systemMessages import CustomMessages
from colorama import Fore

helper = Helpers()
spam_sys_mng = SpamSystemManager()
jail_sys_mgn = JailSystemManager()
jail_manager = JailManagement()
customMessages = CustomMessages()
bot_setup = helper.read_json_file(file_name='mainBotConfig.json')

def is_spam_registered(ctx):
    return spam_sys_mng.check_community_reg_status(community_id=ctx.message.guild.id)

def is_spam_not_registered(ctx):
    return spam_sys_mng.check_if_not_registered(community_id=ctx.message.guild.id)

def is_public(ctx):
    return ctx.message.channel.type != discord.ChannelType.private

def is_overwatch(ctx):
    access_list = [455916314238648340, 360367188432912385]
    return [member for member in access_list if member == ctx.message.author.id]

def is_community_owner(ctx):
    return ctx.message.author.id == ctx.message.guild.owner_id

def is_jail_not_registered(ctx):
    return jail_sys_mgn.check_if_jail_not_registered(community_id=ctx.message.guild.id)


class CommunityOwnerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.check(is_public)
    @commands.check_any(commands.check(is_overwatch), commands.check(is_community_owner))
    async def service(self, ctx):
        """
        Category of commands under team category
        :param ctx:
        :return:
        """

        try:
            await ctx.message.delete()
        except Exception:
            pass

        if ctx.invoked_subcommand is None:
            title = '__Available settings categories for community__'
            description = 'All available commands for owners of the community. Choose one, and further commands will be displayed'
            value = [{'name': f'{bot_setup["command"]}register',
                      'value': "Auto language moderation category of settings for community with auto jail and release function"},
                     {'name': f'{bot_setup["command"]}about',
                      'value': "Information on all services and what the bot offers"}
                     
                     ]

            await customMessages.embed_builder(ctx=ctx, title=title, description=description, data=value)

    @service.command()
    async def about(self, ctx):
        # Create description on all services
        pass
    
    
    @service.group()
    @commands.check(is_public)
    @commands.check_any(commands.check(is_overwatch), commands.check(is_community_owner))
    async def register(self, ctx):
        try:
            await ctx.message.delete()
        except Exception:
            pass

        if ctx.invoked_subcommand is None:
            title = '__Available settings categories for service register__'
            description = 'Before you can use one of the availabale services you need to register it first into the system.'
            value = [{'name': f'{bot_setup["command"]}service register jail',
                      'value': "Register community into the system which automatically monitors use of language, and executes consequences ob breach."},
                     {'name': f'{bot_setup["command"]}service register spam',
                      'value': "Register community for spam service, which prevents community from unwanted discord community bot invasions."}]

            await customMessages.embed_builder(ctx=ctx, title=title, description=description, data=value)
            
    @register.command()
    @commands.check(is_jail_not_registered)
    async def jail(self, ctx):
        if jail_sys_mgn.register_community_for_jail_service(community_id=int(ctx.message.guild.id),
                                                            community_name=f'{ctx.message.guild}',
                                                            owner_id=ctx.message.guild.owner_id,
                                                            owner_name=ctx.message.guild.owner_name):
            
            message = f'You have successfully registered community to ***{self.bot.user.mention} JAIL*** system.'
            await customMessages.system_message(ctx, message=message, color_code=0, destination=1)
        else:
            message = f'There has been an error while trying register community into the JAIL system. Please contact support staff or try again later'
            await customMessages.system_message(ctx, message=message, color_code=0, destination=1)

    
    @register.command()
    @commands.check(is_spam_not_registered)
    async def spam(self, ctx):
        if spam_sys_mng.register_community_for_service(community_id=ctx.message.guild.id, community_name=f'{ctx.message.guild}', owner_id=ctx.message.guild.owner_id,owner_name=f'{ctx.message.author}'):
            message = f'You have successfully registered community to ***{self.bot.user.mention} SPAM*** system.'
            await customMessages.system_message(ctx, message=message, color_code=0, destination=1)
        else:
            message = f'There has been an error while trying register community into the system. Please contact support staff'
            await customMessages.system_message(ctx, message=message, color_code=0, destination=1)

    @service.error
    async def service_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = 'Access to this areas is allowed only for the owner of the community or than the Bot Overwatch members!'
            await customMessages.system_message(ctx, message=message, color_code=1, destination=1)
        else:
            print(error)
            
    @register.error
    async def register_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = 'You are either not an owner of the community, or community has been already registered!'
            await customMessages.system_message(ctx, message=message, color_code=1, destination=1)
        else:
            print(error)
    

def setup(bot):
    bot.add_cog(CommunityOwnerCommands(bot))
