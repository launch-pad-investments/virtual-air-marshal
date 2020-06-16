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
from discord import Embed, Colour, Permissions
from discord import Member as DiscordMember
from discord.ext import commands
from discord.ext.commands import Greedy
from backoffice.jailManagementDb import JailManagement
from utils.jsonReader import Helpers
from cogs.toolsCog.systemMessages import CustomMessages
from cogs.toolsCog.checks import is_public, is_jail_not_registered, is_community_owner, is_spam_not_registered, is_overwatch, is_support_not_registered
from colorama import Fore

helper = Helpers()
spam_sys_mng = SpamSystemManager()
jail_sys_mgn = JailSystemManager()
jail_manager = JailManagement()
custom_message = CustomMessages()
bot_setup = helper.read_json_file(file_name='mainBotConfig.json')
    
class CommunityOwnerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    async def check_role_status(self, ctx, role_name):
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if not role:
            try:
                if role_name == 'Jailed':
                    # Creates the role for Jailed system
                    perms = Permissions(send_messages=False, read_messages=True, view_channel=True, read_message_history = True)
                    await ctx.guild.create_role(name='Jailed', permissions=perms, hoist=True,colour=Colour.red(), mentionable=True)
                elif role_name == 'Visitor':
                    # Creates the role for verified users
                    perms = Permissions(send_messages=False, read_messages=True, view_channel=True,read_message_history = True)
                    await ctx.guild.create_role(name='Visitor', permissions=perms, colour=Colour.green(), mentionable=True)
                elif role_name == 'Unverified':
                    # Creates role for un-verified users
                    perms = Permissions(send_messages=False, read_messages=True, view_channel=True, add_reactions=True)
                    await ctx.guild.create_role(name='Unverified', permissions=perms,colour=Colour.magenta(), mentionable=True)
                return True
            except discord.errors.Forbidden:
                await ctx.channel.send(content='Bot does not have permission to create roles')
                return False
        else:
            print('Role already exists on community')
            return True
        
    @commands.group()
    @commands.bot_has_guild_permissions(administrator=True, manage_messages=True, manage_roles=True)
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
            value = [{'name': f'{bot_setup["command"]}service status',
                      'value': "Register community for spam prevention system for bot invasion"},
                     {'name': f'{bot_setup["command"]}service register spam',
                      'value': "Register community for spam prevention system for bot invasion"},
                     {'name': f'{bot_setup["command"]}service register jail',
                      'value': "Register community for bad language prevention system and auto-jail and un-jail. (IN DEVELOPMENT)"},
                     {'name': f'{bot_setup["command"]}service register support',
                      'value': "Register community for support ticket to the staff members"}
                     ]

            await custom_message.embed_builder(ctx=ctx, title=title, description=description, data=value)

    @service.command()
    @commands.check(is_public)
    @commands.check_any(commands.check(is_overwatch), commands.check(is_community_owner))
    async def status(self, ctx):
        status_embed = Embed(title='__System status__',
                       description='Current status of community on services',
                       colour = Colour.blue())
        if spam_sys_mng.check_if_security_activated(community_id=ctx.message.guild.id) == 1:
            status_embed.add_field(name='Spam prevention system status',
                             value="Activated",
                             inline=False)
        else:
            status_embed.add_field(name='Spam prevention system status',
                    value="Deactivated or not registered",
                    inline=False)
        
        if jail_sys_mgn.get_jail_status(community_id=ctx.message.guild.id) == 1:
            status_embed.add_field(name='Jail and profanity system status',
                    value="Activated",
                    inline=False)
        else:
            status_embed.add_field(name='Spam prevention system status',
                    value="Deactivate or not registered for service",
                    inline=False)
            
        #TODO add support command 
            
        await ctx.channel.send(embed=status_embed)
    
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

            await custom_message.embed_builder(ctx=ctx, title=title, description=description, data=value)
            
    @register.command()
    @commands.check(is_jail_not_registered)
    async def jail(self, ctx):
        if await self.check_role_status(ctx=ctx,role_name='Jailed'):
            if jail_sys_mgn.register_community_for_jail_service(community_id=int(ctx.message.guild.id),
                                                                community_name=f'{ctx.message.guild}',
                                                                owner_id=ctx.message.guild.owner_id,
                                                                owner_name=f'{ctx.message.guild.owner}'):
                
                message = f'You have successfully registered community to ***{self.bot.user.mention} JAIL*** system. Be sure to create role named ***Jailed***'
                await custom_message.system_message(ctx, message=message, color_code=0, destination=1)
            else:
                message = f'There has been an error while trying register community into the JAIL system. Please contact support staff or try again later'
                await custom_message.system_message(ctx, message=message, color_code=0, destination=1)
        else:
            print('Role could not be created')
    
    @register.command()
    @commands.check(is_spam_not_registered)
    async def spam(self, ctx):
        
        if await self.check_role_status(ctx=ctx,role_name='Unverified'):
            if await self.check_role_status(ctx=ctx,role_name='Visitor'):
                if spam_sys_mng.register_community_for_service(community_id=ctx.message.guild.id, community_name=f'{ctx.message.guild}', owner_id=ctx.message.guild.owner_id,owner_name=f'{ctx.message.guild.owner}'):
                    message = f'You have successfully registered community to ***{self.bot.user.mention} SPAM*** system.'
                    await custom_message.system_message(ctx, message=message, color_code=0, destination=1)
                else:
                    message = f'There has been an error while trying register community into the system. Please contact support staff'
                    await custom_message.system_message(ctx, message=message, color_code=0, destination=1)
            else:
                print('Role Verified could not be created')
        else:
            print('Role Unverified could not be created')   
    
    @register.command()
    @commands.check(is_support_not_registered)
    async def support(self, ctx):
        #TODO integrate registration procedure
        pass
    
    
    @service.error
    async def service_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = 'This command is allowed to be executed only on public channel of community'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        if isinstance(error, commands.CheckAnyFailure):
            message = 'Access to this areas is allowed only for the owner of the community or than the Bot Overwatch members!'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        elif isinstance(error,commands.BotMissingPermissions):
            message = 'Bot has insufficient permissions which are required to register for services. It requires at least administrator priileges with message and role management permissions!'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        else:
            dest = await self.bot.fetch_user(user_id=int(360367188432912385))
            await custom_message.bug_messages(ctx=ctx,error=error,destination=dest)
            
    @register.error
    async def register_error(self, ctx, error):
        if isinstance(error, commands.CheckAnyFailure):
            message = 'You are either not an owner of the community, or community has been already registered!'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        elif isinstance(error, commands.CheckFailure):
            message = 'This command is allowed to be executed only on public channel of community'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        else:
            dest = await self.bot.fetch_user(user_id=int(360367188432912385))
            await custom_message.bug_messages(ctx=ctx,error=error,destination=dest)

    @spam.error
    async def spam_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = f'You have already register community for ***SPAM PROTECTION***  system! Proceed with ***{bot_setup["command"]} spam***'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        else:
            dest = await self.bot.fetch_user(user_id=int(360367188432912385))
            await custom_message.bug_messages(ctx=ctx,error=error,destination=dest)
            

    @spam.error
    async def spam_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = f'You have already register community for ***SUPPORT ***  system! Proceed with ***{bot_setup["command"]} support***'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        else:
            dest = await self.bot.fetch_user(user_id=int(360367188432912385))
            await custom_message.bug_messages(ctx=ctx,error=error,destination=dest)
    

def setup(bot):
    bot.add_cog(CommunityOwnerCommands(bot))
