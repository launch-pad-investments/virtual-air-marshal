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
    async def jail(self, ctx, user: discord.Member, duration:int):        
        """
        Sends user to jail
        """
        jail_role = ctx.message.guild.get_role(role_id=710429549040500837)  # Get the jail role
        user_id = user.id
        if jail_role not in user.roles:
            # Current time
            start = datetime.utcnow()

            # Set the jail expiration to after one hour
            td = timedelta(minutes=int(duration))
            # calculate future date
            end = start + td
            expiry = (int(time.mktime(end.timetuple())))
            
            end_date_time_stamp = datetime.utcfromtimestamp(expiry)

            # Get all roles user has                                                                                    
            guild = self.bot.get_guild(id=667607865199951872)  # Get guild
            active_roles = [role.id for role in user.roles][1:] # Get active roles
            if jail_manager.throw_to_jail(discord_id=int(user_id),end=expiry, roleIds=active_roles):
                if jail_manager.check_if_in_counter(discord_id=int(user.id)):
                    jail_manager.remove_from_counter(discord_id=int(user_id))
                
                guild = self.bot.get_guild(id=667607865199951872)
                
                await user.add_roles(jail_role, reason='Jailed......')       
                print(Fore.RED + f'User {user} has been jailed by Admin!!!!')
                
                
                # Send message
                jailed_info = discord.Embed(title='__You have been jailed by Admin!__',
                                            description=f'You have been manually jailed by Admin {ctx.message.author}.'
                                            'All roles on community have been removed and will be automatically reasigned once jail time is served',
                                            color = discord.Color.red())
                jailed_info.add_field(name=f'Jail time duration:',
                                    value=f'{duration} minutes')
                jailed_info.add_field(name=f'Sentence started @:',
                                    value=f'{start} UTC')
                jailed_info.add_field(name=f'Sentece ends on:',
                                    value=f'{end_date_time_stamp} UTC')                
                await user.send(embed=jailed_info)
                await ctx.channel.send(content=':cop:', delete_after = 60)
                
                # Remove all other roles from user
                for role in active_roles:
                    role = guild.get_role(role_id=int(role))  # Get the role
                    await user.remove_roles(role, reason='Jail time initiated')
                    
                message=f'{ctx.message.author} Jailed {user} for {duration} mininutes! :soap: :eggplant: '
                await customMessages.system_message(ctx=ctx, color_code=0, destination=1, message=message)
                    
            else:
                print('Could not throw him to database jail')
        else:
            message=f'{user} Is Jailed already...'
            await customMessages.system_message(ctx=ctx, color_code=1, destination=1, message=message)
 
    
    @admin.command()
    @commands.check(is_public)
    async def release(self, ctx, user:discord.Member):
        if jail_manager.check_if_jailed(discord_id = int(user.id)):
            user_details = jail_manager.get_jailed_user(discord_id=user.id)
            if jail_manager.remove_from_jailed(discord_id=int(user.id)):
                all_role_ids = user_details["roleIds"]
                free = discord.Embed(title='__Sentence Revoked__',
                        color=discord.Color.green())
                free.set_thumbnail(url=self.bot.user.avatar_url)
                free.add_field(name='Message',
                               value='You have been manually unjailed by {ctx.message.author} and you can start to communicate again! '
                               ' Next time be more caucious what and how you write. Bad behaviour will'
                               ' not be tolerated')
                await user.send(embed=free)
                
                # Add all roles user has had in the past
                for taken_role in all_role_ids:
                        to_give=ctx.message.guild.get_role(role_id=int(taken_role))
                        if to_give:
                            await user.add_roles(to_give, reason='Returning back roles')    

                # Get and remove jailed role
                role = ctx.message.guild.get_role(role_id=710429549040500837)  # Get the jail role           
                         
                if role: 
                    if role in user.roles:
                        await user.remove_roles(role, reason='Jail time served')
                        
                time_of_release = datetime.utcnow()
                print(Fore.GREEN + f'@{time_of_release} --> {user} has been unjailed by {ctx.message.author}')        
            else:
                message=f'{user} Could not be set free due to system error...'
                await customMessages.system_message(ctx=ctx, color_code=1, destination=1, message=message) 
        else:
            message=f'{user} Is not jailed at this moment...'
            await customMessages.system_message(ctx=ctx, color_code=1, destination=1, message=message) 
            
    
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
