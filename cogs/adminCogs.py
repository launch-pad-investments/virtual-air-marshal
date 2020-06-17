import os
import sys

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

from datetime import datetime
from datetime import timedelta
import time
import discord
from discord import Member as DiscordMember
from discord.ext import commands
from discord.ext.commands import Greedy
from backoffice.jailManagementDb import JailManagement
from utils.jsonReader import Helpers
from cogs.toolsCog.systemMessages import CustomMessages
from colorama import Fore

helper = Helpers()
jail_manager = JailManagement()
customMessages = CustomMessages()
bot_setup = helper.read_json_file(file_name='mainBotConfig.json')


class custom_checks:
    @staticmethod
    def superior(member1, member2):
        if member1.top_role.position > member2.top_role.position:
            return member1
        elif member1.top_role.position < member2.top_role.position:
            return member2


def is_overwatch(ctx):
    access_list = bot_setup['userAccess']
    return [user for user in access_list if ctx.message.author.id == user]


def role_mng(ctx):
    return ctx.author.manage_roles


def ban_predicate(ctx):
    return ctx.author.guild_permissions.ban_members


def kick_predicate(ctx):
    return ctx.author.guild_permissions.kick_members


def admin_predicate(ctx):
    return ctx.message.author.administrator


def is_public(ctx):
    return ctx.message.channel.type != discord.ChannelType.private


class TeamCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.check(is_public)
    @commands.check_any(commands.is_owner(), commands.check(kick_predicate), commands.check(admin_predicate),
                        commands.check(ban_predicate), commands.check(is_overwatch))
    async def admin(self, ctx):
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
            title = 'Admin available commands'
            description = 'All available commands for administrators of the community.'
            value = [{'name': f'{bot_setup["command"]} kick <list of users> <reason>',
                      'value': f"Kicks selected user/users and provides reason. requires to have *kick_members*"
                               f" permission"},
                     {'name': f'{bot_setup["command"]} ban <list of users> <reason>',
                      'value': f"Bans the selected users and deletes messages for past 7 days. Requires to have"
                               f" *ban_members* permission"},
                     {'name': f'{bot_setup["command"]} add_role <@discord.User> <#discord.Role to give>',
                      'value': f"Adds role to the user"},
                     {'name': f'{bot_setup["command"]} remove_role <@discord.User> <#discord.Role to give>',
                      'value': f"Remove role from user"}
                     ]

            await customMessages.embed_builder(ctx=ctx, title=title, description=description, data=value)

    @commands.command()
    @commands.check(is_public)
    @commands.check_any(commands.is_owner(), commands.check(kick_predicate), commands.check(admin_predicate),
                        commands.check(is_overwatch))
    async def kick(self, ctx, users: Greedy[DiscordMember], *, reason: str):
        """
        Kicks the member from the community
        :param ctx:
        :param users:
        :param reason:
        :return:
        """
        if ctx.author.guild_permissions.kick_members:
            kicked_members = ''
            for user in users:
                if ctx.author is custom_checks.superior(ctx.author, user):
                    kick_msg = f"You have been kicked from *** {ctx.guild.name} *** by ***{ctx.author.name}***.\n" \
                               f"because of: {reason} "
                    await customMessages.user_message(message=kick_msg,
                                                      description='Marshal took action',
                                                      color_code=1,
                                                      to_user=user)
                    kicked_members += f'{user.name} with ID: {user.id}\n'
                    await user.kick(reason=reason)

            await customMessages.system_message(ctx=ctx,
                                                color_code=0,
                                                message=kicked_members,
                                                destination=0,
                                                sys_msg_title='Members kicked')
        else:
            message = ' You do not have permission to kick members. Contact one of the admins who has'
            await customMessages.system_message(ctx=ctx,
                                                color_code=1,
                                                message=message,
                                                destination=0,
                                                sys_msg_title='Kicking failed')

    @commands.command()
    @commands.check(is_public)
    @commands.check_any(commands.is_owner(), commands.check(ban_predicate), commands.check(admin_predicate),
                        commands.check(is_overwatch))
    async def ban(self, ctx, users: Greedy[DiscordMember], *, reason: str):
        """
        Bans the member from the community
        :param ctx:
        :param users:
        :param reason:
        :return:
        """
        if ctx.author.guild_permissions.ban_members:
            kicked_members = ''
            for user in users:
                if ctx.author is custom_checks.superior(ctx.author, user):
                    ban_msg = f"You have been baned from *** {ctx.guild.name} *** by ***{ctx.author.name}***.\n" \
                              f"because of: {reason} "
                    await customMessages.user_message(message=ban_msg,
                                                      description='Marshal took action!',
                                                      color_code=1,
                                                      to_user=user)
                    kicked_members += f'{user.name} with ID: {user.id}\n'
                    await user.ban(reason=reason, days_to_delete=7)

            await customMessages.system_message(ctx=ctx,
                                                color_code=0,
                                                message=kicked_members,
                                                destination=0,
                                                sys_msg_title='Members Banned')
        else:
            message = ' You do not have permission to ban members. Contact one of the admins who has!'
            await customMessages.system_message(ctx=ctx,
                                                color_code=1,
                                                message=message,
                                                destination=0,
                                                sys_msg_title='Kicking failed')

    @commands.command()
    @commands.check(is_public)
    @commands.check_any(commands.is_owner(), commands.check(role_mng), commands.check(admin_predicate))
    async def remove_role(self, ctx, user: discord.Member, role: discord.Role):
        await user.remove_roles(role, reason='Naught boy')
        message = f'Role {role.name} with ID {role.id}has ben removed from {user.display_name}'
        await customMessages.system_message(ctx=ctx, color_code=0, destination=1, message=message)

    @commands.command()
    @commands.check(is_public)
    @commands.check_any(commands.is_owner(), commands.check(role_mng), commands.check(admin_predicate))
    async def add_role(self, ctx, user: discord.Member, role: discord.Role):
        await user.add_roles(role, reason='Role given')
        message = f'Role {role.name} with ID {role.id}has ben given to the user {user.display_name}'
        await customMessages.system_message(ctx=ctx, color_code=0, destination=1, message=message)

    @commands.group()
    @commands.check(is_public)
    @commands.check_any(commands.is_owner(),commands.check(admin_predicate))
    async def create(self, ctx):
        pass
    
    @create.command()
    async def text_channel(self, ctx, channel_name:str, *, channel_topic:str=None):
        try:
            await ctx.message.delete()
        except Exception:
            pass
        
        try:
            channel = await ctx.guild.create_text_channel(name=channel_name, topic=channel_topic)
            await channel.send(content=f'{ctx.author.mention} you have successfully created new Text Channel!')
        except discord.Forbidden as e:
            message = f'Voice Channel could not be created.. Here are details {e}.'
            await customMessages.system_message(ctx, message=message, color_code=1, destination=1)
        except discord.HTTPException as e:
            message = f'Voice Channel could not be created.. Here are details {e}.'
            await customMessages.system_message(ctx, message=message, color_code=1, destination=1)
        except discord.InvalidArgument as e:
            message = f'Voice Channel could not be created.. Here are details {e}.'
            await customMessages.system_message(ctx, message=message, color_code=1, destination=1)

    @create.command()
    async def voice_channel(self, ctx, channel_name:str, *, channel_topic:str=None):
        try:
            await ctx.message.delete()
        except Exception:
            pass
        
        try:
            channel = await ctx.guild.create_voice_channel(name=channel_name, topic=channel_topic)
        except discord.Forbidden as e:
            message = f'Voice Channel could not be created.. Here are details {e}.'
            await customMessages.system_message(ctx, message=message, color_code=1, destination=1)
        except discord.HTTPException as e:
            message = f'Voice Channel could not be created.. Here are details {e}.'
            await customMessages.system_message(ctx, message=message, color_code=1, destination=1)
        except discord.InvalidArgument as e:
            message = f'Voice Channel could not be created.. Here are details {e}.'
            await customMessages.system_message(ctx, message=message, color_code=1, destination=1)


    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            message = 'You have provided bad argument. When selecting users, they need to be tagged.'
            await customMessages.system_message(ctx, message=message, color_code=1, destination=1)
        elif isinstance(error, commands.MissingRequiredArgument):
            message = f'You forgot to provide all arguments for the kick command. Command structure is' \
                      f' {bot_setup["command"]}admin kick <user/users> <reason>.'
            await customMessages.system_message(ctx, message=message, color_code=1, destination=1)

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            message = 'You have provided bad argument. When selecting users, they need to be tagged.'
            await customMessages.system_message(ctx, message=message, color_code=1, destination=1)
        elif isinstance(error, commands.MissingRequiredArgument):
            message = f'You forgot to provide all arguments for the ban command. Command structure is' \
                      f' {bot_setup["command"]}admin ban <user/users list> <reason>.'
            await customMessages.system_message(ctx, message=message, color_code=1, destination=1)


def setup(bot):
    bot.add_cog(TeamCommands(bot))
