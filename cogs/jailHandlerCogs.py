import os
import sys

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

from datetime import datetime
from datetime import timedelta
import time
import discord
from discord import Member

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


class JailService(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.command = bot_setup['command']

    @commands.group()
    @commands.check(is_public)
    @commands.bot_has_guild_permissions(administrator=True, manage_messages=True, manage_roles=True)
    @commands.check_any(commands.has_guild_permissions(administrator=True), commands.check(is_overwatch),
                        commands.check(is_community_owner))
    async def jail(self, ctx):
        """
        Entry point for jail actions.

        Args:
            ctx (discord.Context)
        """
        if ctx.invoked_subcommand is None:
            title = '__Available commands under ***Jail*** category!__'
            description = 'With jail system, with administrative rights, user can put another member to jail for ' \
                          'N amount of time. System handles on its own jail release and returning of perks from pre-' \
                          'jail time upon expirations'

            value = [{'name': f'Activate jail',
                      'value': f'```{self.command}jail on```'},
                     {'name': f'Deactivate jail',
                      'value': f'```{self.command}jail off```'},
                     {'name': f'Release members sooner manually',
                      'value': f'```{self.command}jail release <@discord.User>```'},
                     {'name': f'Send member to jail',
                      'value': f'```{self.command}jail punish <@discord.User> <duration in minutes>```'}
                     ]

            await custom_message.embed_builder(ctx=ctx, title=title, description=description, data=value)

    @jail.command()
    @commands.check(is_community_registered)
    async def on(self, ctx):
        """
        Command turns the jail and profanity system ON

        Args:
            ctx (discord.Context)
        """
        if jail_sys_manager.turn_on_off(community_id=int(ctx.message.guild.id), direction=1):
            title = '__System Message__'
            message = 'You have turned ON the automatic jail system and profanity monitor successfully. '
            await custom_message.system_message(ctx=ctx, color_code=0, message=message, destination=1,
                                                sys_msg_title=title)
        else:
            message = f'There was a backend error. Please try again later or contact one of the administrators on the community. We apologize for inconvinience'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)

    @jail.command()
    @commands.check(is_community_registered)
    async def off(self, ctx):
        """
        Command turns the jail and profanity system OFF

        Args:
            ctx (discord.Context)
        """
        if jail_sys_manager.turn_on_off(community_id=int(ctx.message.guild.id), direction=0):
            title = '__System Message__'
            message = 'You have turned OFF automtic jail system and profanity successfully. Your members can get crazy'
            await custom_message.system_message(ctx=ctx, color_code=0, message=message, destination=1,
                                                sys_msg_title=title)
        else:
            message = f'There was a backend error. Please try again later or contact one of the administrators on the community. We apologize for inconvinience'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)

    @jail.command()
    @commands.check(is_public)
    @commands.check_any(commands.check(is_overwatch), commands.check(is_community_owner))
    async def release(self, ctx, user: Member):
        """
        Allows user with either overwatch or community owner rights to release discord member from the jail.

        Args:
            ctx (dscrod.Context): 
            user (discord.Member): 
        """
        # Check if member in jail
        if jail_manager.check_if_jailed(user_id=user.id, community_id=ctx.guild.id):
            user_details = jail_manager.get_jailed_user(discord_id=user.id)
            if user_details:
                if jail_manager.remove_from_jailed(discord_id=user.id):
                    release = datetime.utcnow()
                    all_role_ids = user_details["roleIds"]
                    free = discord.Embed(title='__Jail message__',
                                         color=discord.Color.green())
                    free.set_thumbnail(url=self.bot.user.avatar_url)
                    free.add_field(name='Time of release',
                                   value=f'{release}',
                                   inline=False)
                    free.add_field(name='Message',
                                   value=f'You have been manually released from jail by the {ctx.message.author} '
                                         f'on {ctx.message.guild}')
                    await user.send(embed=free)

                    free = discord.Embed(title='__Jail message__',
                                         color=discord.Color.green())
                    free.set_thumbnail(url=self.bot.user.avatar_url)
                    free.add_field(name='Time of release',
                                   value=f'{release}',
                                   inline=False)
                    free.add_field(name='Message',
                                   value=f'You have successfully released from jail {user} on {ctx.message.guild}')
                    await user.send(embed=free)

                    # Check if member still exists
                    if all_role_ids:
                        for taken_role in all_role_ids:
                            to_give = ctx.message.guild.get_role(role_id=int(taken_role))
                            if to_give:
                                await user.add_roles(to_give, reason='Returning back roles')

                    role_rmw = discord.utils.get(ctx.guild.roles, name="Jailed")

                    if role_rmw:
                        if role_rmw in user.roles:
                            await user.remove_roles(role_rmw, reason='Jail time served')

                    print(
                        Fore.LIGHTGREEN_EX + f"{user} Successfully released from jail on {ctx.message.guild} "
                                             f"and state restored ")

                    message = f'You have successfully release {user} from the jail, and his' \
                              f' pre-jail perks have been returned.'
                    await custom_message.system_message(ctx, message=message, color_code=0, destination=1)
                else:
                    message = f'User {user} could not be release from jail due to system error. Please try again later. '
                    await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
            else:
                message = f'User {user} is not jailed at this moment. '
                await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        else:
            message = f'User {user} is not jailed at this moment. '
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)

    @jail.command()
    @commands.check(is_public)
    @commands.check(is_community_registered)
    @commands.check_any(commands.check(is_overwatch), commands.check(is_community_owner))
    async def punish(self, ctx, jailee: Member, duration: int, *, subject: str = None):
        # Current time
        start = datetime.utcnow()
        # Set the jail expiration to after N minutes
        td = timedelta(minutes=int(duration))

        # calculate future date
        end = start + td
        expiry = (int(time.mktime(end.timetuple())))
        end_date_time_stamp = datetime.utcfromtimestamp(expiry)

        # guild = self.bot.get_guild(id=int(message.guild.id))  # Get guild
        if ctx.author.top_role.position >= jailee.top_role.position:
            active_roles = [role.id for role in jailee.roles][1:]  # Get active roles
            if jailee.id != ctx.message.guild.owner_id:
                if not jailee.bot:
                    if ctx.author.id != jailee.id:
                        # jail user in database
                        if not jail_manager.check_if_jailed(user_id=int(jailee.id), community_id=ctx.guild.id):
                            if jail_manager.throw_to_jail(user_id=jailee.id, community_id=ctx.guild.id,
                                                          expiration=expiry, role_ids=active_roles):

                                # Remove user from active counter database
                                if jail_manager.remove_from_counter(discord_id=int(jailee.id)):

                                    # Send message
                                    jailed_info = discord.Embed(title='__You have been jailed!__',
                                                                description=f' You have been manually jailed by '
                                                                            f'{ctx.message.author} on {ctx.guild} for '
                                                                            f'{duration} minutes. Status will be restored '
                                                                            f'once Jail Time Expires.',
                                                                color=discord.Color.red())
                                    jailed_info.set_thumbnail(url=self.bot.user.avatar_url)
                                    jailed_info.add_field(name=f'Reason',
                                                          value=f'{subject}',
                                                          inline=False)
                                    jailed_info.add_field(name=f'Jail time duration:',
                                                          value=f'{duration} minutes',
                                                          inline=False)
                                    jailed_info.add_field(name=f'Sentence started @:',
                                                          value=f'{start} UTC',
                                                          inline=False)
                                    jailed_info.add_field(name=f'Jail-time ends on:',
                                                          value=f'{end_date_time_stamp} UTC',
                                                          inline=False)
                                    jailed_info.set_thumbnail(url=self.bot.user.avatar_url)
                                    await jailee.send(embed=jailed_info)

                                    # Send notf to user who executed
                                    executor = discord.Embed(title='__User Jailed__',
                                                             description=f' You have successfully jailed {jailee} on '
                                                                         f'{ctx.guild} for {duration} minutes. Status '
                                                                         f'will be restored once Jail Time Expires.',
                                                             color=discord.Color.red())
                                    executor.set_thumbnail(url=self.bot.user.avatar_url)
                                    executor.add_field(name=f'Reason',
                                                       value=f'{subject}',
                                                       inline=False)
                                    executor.add_field(name=f'Jailed User:',
                                                       value=f'{jailee} \n id: {jailee.id}',
                                                       inline=False)
                                    executor.add_field(name=f'Jail time duration:',
                                                       value=f'{duration} minutes',
                                                       inline=False)
                                    executor.add_field(name=f'Sentence started @:',
                                                       value=f'{start} UTC',
                                                       inline=False)
                                    executor.add_field(name=f'Sentece ends on:',
                                                       value=f'{end_date_time_stamp} UTC',
                                                       inline=False)
                                    executor.set_thumbnail(url=self.bot.user.avatar_url)

                                    # Send notf to channel
                                    await ctx.author.send(embed=executor)

                                    # ADD Jailed role to user
                                    role = discord.utils.get(ctx.guild.roles, name="Jailed")
                                    await jailee.add_roles(role, reason='Jailed......')
                                    print(
                                        Fore.RED + f'User {jailee} has been jailed by {ctx.message.author} '
                                                   f'on {ctx.message.guild.id}!!!!')
                                    print(Fore.GREEN + 'Removing active roles from user')
                                    for role in active_roles:
                                        role = ctx.guild.get_role(role_id=int(role))  # Get the role
                                        await jailee.remove_roles(role, reason='Jail time')
                            else:
                                title = '__Manual Jail Function Error__'
                                message = f'Member {jailee} could not be jailed at this moment' \
                                          f' due to the backend system error!'
                                await custom_message.system_message(ctx, message=message, color_code=1, destination=1,
                                                                    sys_msg_title=title)
                        else:
                            title = '__User already Jailed!__'
                            message = f'Member {jailee} is already jailed!'
                            await custom_message.system_message(ctx, message=message, color_code=1, destination=1,
                                                                sys_msg_title=title)
                    else:
                        title = '__Jail error!__'
                        message = f'Why would someone want to jail himself?'
                        await custom_message.system_message(ctx, message=message, color_code=1, destination=1,
                                                            sys_msg_title=title)
                else:
                    title = '__Jail error!__'
                    message = f'AI Sticks together... You cant jail {jailee} as it is a bot!'
                    await custom_message.system_message(ctx, message=message, color_code=1, destination=1,
                                                        sys_msg_title=title)
            else:
                title = '__Jail error!__'
                message = f'Owner of the guild can not be jailed!'
                await custom_message.system_message(ctx, message=message, color_code=1, destination=1,
                                                    sys_msg_title=title)
        else:
            title = '__Jail error!__'
            message = f'You cant jail member who has higher ranked role than you.'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1, sys_msg_title=title)

    @jail.error
    async def jail_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = f'Command is allowed to be executed only on the public channels of the {ctx.message.guild}' \
                      f' and community needs to be registered into the ***JAIL*** system.'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        if isinstance(error, commands.CheckAnyFailure):
            message = f'In order to use jail on {ctx.guild} you either need to be on ***Overwatch roster, owern ' \
                      f'of the community or have administrator*** rights!.'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        elif isinstance(error, commands.BotMissingPermissions):
            message = 'Bot has insufficient permissions which are required to register for services. It requires at ' \
                      'least administrator priileges with message and role management permissions!'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)

    @punish.error
    async def punish_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = f'***ERROR{error}*** \nThis error occured from possible reasons:\n--> Command not executed ' \
                      f'on public channels of the {ctx.message.guild}\n --> jail service not ' \
                      f'registered ({self.bot.user.mention} service)'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        elif isinstance(error, commands.CheckAnyFailure):
            message = f'In order to use jail on {ctx.guild} you either need to be on ***Overwatch*** roster, owner' \
                      f'of the community or have administrator*** rights!.'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        elif isinstance(error, commands.BadArgument):
            message = f'Wrong argument provided:\n __{error}__. \nCommand structure is:\n***{self.bot.user.mention} ' \
                      f'jail punish <@discord.User> <duration in minutes>***'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        elif isinstance(error, commands.MissingRequiredArgument):
            message = f'You forgot to provide all required arguments. \n***{self.bot.user.mention} jail punish ' \
                      f'<@discord.User> <duration in minutes> <message=Optional>***'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        else:
            title = '__:bug: Found__'
            message = f'Bug has been found while executing command and {self.bot.user} service team has been ' \
                      f'automatically notified. We apologize for inconvenience!'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1, sys_msg_title=title)
            dest = await self.bot.fetch_user(user_id=int(360367188432912385))
            await custom_message.bug_messages(ctx=ctx, error=error, destination=dest)

    @release.error
    async def release_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = f'Command is allowed to be executed only on the public channels of the {ctx.message.guild}.'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        elif isinstance(error, commands.CheckAnyFailure):
            message = f'You do not have rights to access this area of {self.bot.user.mention} on {ctx.message.guild}.'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        elif isinstance(error, commands.BadArgument):
            message = f'Wrong argument provided:\n {error}.\n Command structure is:\n ***{self.bot.user.mention} ' \
                      f'jail release <@discord.User>***'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        else:
            title = '__:bug: Found__'
            message = f'Bug has been found while executing command and {self.bot.user} service team has been' \
                      f' automatically notified. We apologize for inconvenience!'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1, sys_msg_title=title)
            dest = await self.bot.fetch_user(user_id=int(360367188432912385))
            await custom_message.bug_messages(ctx=ctx, error=error, destination=dest)

    @on.error
    async def on_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = f'{ctx.guild} has not been registered yet for ***JAIL*** service. Please start' \
                      f' with ***{self.bot.mention} service register jail***'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)

    @off.error
    async def off_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = f'{ctx.guild} has not been registered yet for ***JAIL*** service. ' \
                      f'Please start with ***{bot_setup["command"]} service register jail***'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)


def setup(bot):
    bot.add_cog(JailService(bot))
