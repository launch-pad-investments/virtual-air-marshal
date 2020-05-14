import os
import sys

import discord
from discord import Member as DiscordMember
from discord.ext import commands
from discord.ext.commands import Greedy

from utils.jsonReader import Helpers
from .toolsCog.systemMessages import CustomMessages

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

helper = Helpers()

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
            value = [{'name': f'{bot_setup["command"]}admin kick <list of users> <reason>',
                      'value': f"Kicks selected user/users and provides reason. requires to have *kick_members*"
                               f" permission"},
                     {'name': f'{bot_setup["command"]}admin ban <list of users> <reason>',
                      'value': f"Bans the selected users and deletes messages for past 7 days. Requires to have"
                               f" *ban_members* permission"},
                     {'name': f'{bot_setup["command"]}admin check',
                      'value': f"Sub category of admin to query various data from the user. Use"
                               f" ***{bot_setup['command']}admin check*** to get data on available sub-commands"},
                     ]

            await customMessages.embed_builder(ctx=ctx, title=title, description=description, data=value)

    @admin.command()
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

    @admin.command()
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

    @admin.command()
    @commands.check(is_public)
    @commands.check_any(commands.is_owner(), commands.check(role_mng), commands.check(admin_predicate))
    async def remove_role(self, ctx, user: discord.Member, role: discord.Role):
        await user.remove_roles(role, reason='Naught boy')
        message = f'Role {role.name} with ID {role.id}has ben removed from {user.display_name}'
        await customMessages.system_message(ctx=ctx, color_code=0, destination=1, message=message)

    @admin.command()
    @commands.check(is_public)
    @commands.check_any(commands.is_owner(), commands.check(role_mng), commands.check(admin_predicate))
    async def add_role(self, ctx, user: discord.Member, role: discord.Role):
        await user.add_roles(role, reason='Role given')
        message = f'Role {role.name} with ID {role.id}has ben given to the user {user.display_name}'
        await customMessages.system_message(ctx=ctx, color_code=0, destination=1, message=message)

    @admin.group()
    @commands.check(is_public)
    @commands.check_any(commands.is_owner(), commands.check(admin_predicate), commands.check(ban_predicate))
    async def check(self, ctx):
        if ctx.invoked_subcommand is None:
            title = f"Sub commands for ***{bot_setup['command']}admin check*** group"
            description = f"Description of all availabale sub-command for __check__ category"
            value = [{'name': f'{bot_setup["command"]}admin check user_info <Discord Member>  ',
                      'value': f"Returns indepth details about the user"},
                     {'name': f'{bot_setup["command"]}admin check user_roles <Discord Member> ',
                      'value': f"Returns all the roles which are applied to selected member"},
                     {'name': f'{bot_setup["command"]}admin check user_guild_permissions <Discord Member> ',
                      'value': f"Returns users global guild permissions"},
                     {
                         'name': f'{bot_setup["command"]}admin check user_channel_permissions <Discord Member> <Discord Channel> ',
                         'value': f"Checks the permissions user has for selected channel"},
                     ]
            await customMessages.embed_builder(ctx=ctx, title=title, description=description, data=value)

    @check.command()
    async def user_roles(self, ctx, user: DiscordMember):
        """
        Checks waht roles user has
        :param ctx: Discord Context
        :param user: Discord Member
        :return: info embed on roles
        """
        title = f"Role query"
        description = f'Role and permission check for user {user.name} with ID {user.id}'
        roles = ''
        for role in user.roles:
            roles += f'{role.name}\n'

        value = [{'name': f'Roles for user {user.name} with ID {user.id}',
                  'value': f"{roles}"}
                 ]

        await customMessages.embed_builder(ctx, title=title, description=description, data=value)

    @check.command()
    async def user_info(self, ctx, user: DiscordMember):
        # TODO does not work

        roles = f'***Top Role: {user.top_role}***'
        for role in user.roles[1:]:
            roles += f'{role.name}\n'

        if user.premium_since is None:
            premium = "No Premium status"
        else:
            premium = user.premium_since

        act = ''
        count = 1
        if user.activities is not None:
            for activity in user.activities:
                act += f'{count}.: {activity}\n'
                count += 1
        else:
            act = 'User does not have activities'

        user_info = discord.Embed(title='User Info',
                                  description='info on the user')
        user_info.set_thumbnail(url=user.avatar_url)
        user_info.add_field(name='__**User:**__',
                            value=f'Username: ***{user}***\n'
                                  f'User ID: ***{user.id}***\n'
                                  f'Display Name: ***{user.display_name}***\n'
                                  f'Nickname: ***{user.nick}***',
                            inline=False)
        user_info.add_field(name='Account created:',
                            value=user.created_at,
                            inline=False)
        user_info.add_field(name='Joined community at',
                            value=user.joined_at,
                            inline=True)
        user_info.add_field(name='Is Bot',
                            value=user.bot,
                            inline=False)
        user_info.add_field(name='Premium status',
                            value=premium,
                            inline=False)
        user_info.add_field(name='Current status',
                            value=user.status,
                            inline=False)
        user_info.add_field(name=f'Roles on {user.guild}',
                            value=roles)
        user_info.add_field(name='Current activities:',
                            value=act,
                            inline=False)
        user_info.add_field(name='Voice state',
                            value=user.voice)
        user_info.add_field(name='Guild',
                            value=user.guild.name,
                            inline=False)
        await ctx.channel.send(embed=user_info)

    @check.command()
    async def user_guild_permissions(self, ctx, user: DiscordMember):
        """
        Returs users global guild permissions
        :param ctx: Discord Context
        :param user: Discord User/ Mmember
        :return:
        """
        user_perm = ''
        for perm in user.guild_permissions:
            if perm[1] is True:
                user_perm += f"- {perm[0]}\n"
        values = [
            {"name": f"Users general permissions on  ***#{user.guild.name}***",
             "value": user_perm}
        ]
        await customMessages.embed_builder(ctx, title="Guild Permission check",
                                           description=f"{user.name} with ID {user.id} permission status for channel",
                                           data=values)

    @check.command()
    async def user_channel_permissions(self, ctx, user: DiscordMember, channel: discord.TextChannel):
        """
        Checks the permissions of the user for selected channell
        :param ctx: Context
        :param user: Discord User
        :param channel: Discord Channel
        :return: Info Embed
        """
        user_perm = ''
        for perm in user.permissions_in(channel):
            if perm[1] is True:
                user_perm += f"- {perm[0]}\n"
        values = [
            {"name": f"Permissions for channel ***#{channel.name}***",
             "value": user_perm}
        ]
        await customMessages.embed_builder(ctx, title="Channel Permission check",
                                           description=f"{user.name} with ID {user.id} permission status for channel",
                                           data=values)

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
