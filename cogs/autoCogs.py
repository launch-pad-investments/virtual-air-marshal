import os
import sys
from datetime import datetime

from colorama import Fore, init
from discord import Embed, Colour
from discord import TextChannel, utils
from discord.ext import commands

from backoffice.jailManagementDb import JailManagement
from backoffice.jailSystemDb import JailSystemManager
from backoffice.loggerSystemDb import LoggerSystem
from backoffice.spamSystemDb import SpamSystemManager
from backoffice.supportSystemDb import SupportSystemManager
from cogs.toolsCog.systemMessages import CustomMessages
from utils.jsonReader import Helpers

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

init(autoreset=True)

jail_manager = JailManagement()
helper = Helpers()
custom_messages = CustomMessages()
spam_sys_mng = SpamSystemManager()
jail_sys_mng = JailSystemManager()
sup_sys_mng = SupportSystemManager()
logger = LoggerSystem()

bot_setup = helper.read_json_file(file_name='mainBotConfig.json')
CONST_JAIL_DURATION = 5


class AutoFunctions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Print out to console once bot logs in
        :return:
        """
        print(
            Fore.LIGHTYELLOW_EX + '===================================\nLogging in...\n===================================')
        print(Fore.LIGHTGREEN_EX + 'Logged in as:')
        print(Fore.LIGHTGREEN_EX + f'Username: {self.bot.user.name}')
        print(Fore.LIGHTGREEN_EX + f'User ID: {self.bot.user.id}')
        guilds = await self.bot.fetch_guilds(limit=150).flatten()
        reach = len(self.bot.users)
        print(Fore.LIGHTGREEN_EX + f'Integrated into: {len(guilds)} guilds')
        print(Fore.LIGHTGREEN_EX + f'Member reach: {reach} members')

        print(f'==============DONE=================')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        When member joins community bot will recognize it and activates spam protection proceddure
        Args:
            member (discord.Member): Member which joines the community
        """
        print(Fore.LIGHTYELLOW_EX + f'{member} joining {member.guild} ')
        if spam_sys_mng.check_community_reg_status(community_id=member.guild.id):
            if not member.bot:
                sec_value = spam_sys_mng.check_if_security_activated(community_id=int(member.guild.id))
                details = spam_sys_mng.get_details_of_channel(
                    community_id=member.guild.id)  # Get details of channel as dict

                if sec_value == 1:
                    role = utils.get(member.guild.roles,
                                     name="Unverified")  # Check if role can be found if not than None
                    if role:
                        await member.add_roles(role)  # Give member a role
                        # Console printoutn
                        print(Fore.BLUE + f"New user joined community: {member} (ID: {member.id})")
                        print(Fore.YELLOW + f"Role Unverified given to the user {member} with ID: {member.id}")
                        text = f'Hey and welcome to the {member.guild}. Community has activate __spam prevention system__ ' \
                               f'which requires from newly joined users o verify themselves. Head to channel ' \
                               f'#{details["appliedChannelName"]} (ID: {details["appliedChannelId"]}) and accept ' \
                               f'TOS/Rules of community by reacting to the message with :thumbsup: ! If ' \
                               f'successful, community channels will become availabale for you.'

                        sys_embed = Embed(title="__Air Marshal Auto-System Message__",
                                          description="This is auto-message!",
                                          colour=0x319f6b)
                        sys_embed.add_field(name=':warning: Message: warning: ',
                                            value=text,
                                            inline=False)
                        sys_embed.set_thumbnail(url=self.bot.user.avatar_url)
                        sys_embed.set_footer(text='Virtual Air Marshal is watching')

                        try:
                            await member.send(embed=sys_embed)
                            print(Fore.YELLOW + f"Message with instructions sent to {member} with ID: {member.id}")
                        except Exception:
                            print(
                                Fore.RED + f"Message with instructions could not be delivered to {member} with ID: {member.id} due to no DM rule")
                            pass
                    else:
                        print(
                            Fore.RED + f"Role Unverified does not eexist on guild {member.guild} with id {member.guild.id}")

                        # Give user verified role
                elif sec_value == 0:
                    # Auto role if system is off
                    print(Fore.BLUE + f"New user joined community: {member} (ID: {member.id})")
                    role = utils.get(member.guild.roles, name='Visitor')

                    if role:
                        await member.add_roles(role)

                        print(Fore.YELLOW + f"Role Visitor given to the user {member} with ID: {member.id}")
                        text = f'Hey and welcome to the {member.guild}. '
                        f'Head to channel #{details["appliedChannelName"]} '
                        f'(ID: {details["appliedChannelId"]}) and familiarize yourself with TOS/Rules of ' \
                        f'community and enjoy jour stay!'

                        sys_embed = Embed(title=":rocket: __Air Marshal System Message__ :rocket:",
                                          description=f"Access to {member.guild} granted!",
                                          colour=0x319f6b)
                        sys_embed.add_field(name='__Notice!__',
                                            value=text)

                        try:
                            await member.send(embed=sys_embed)
                        except Exception:
                            print('pass')

                        text = f'{member.guild} uses {self.bot.user} which is a product ' \
                               f'of Launch Pad Investment Discord Group. '
                        f' It has been designed with the reason to allow moderation of the community.'

                        sys_embed = Embed(title=":rocket: __Air Marshal System Message__ :rocket:",
                                          description=f"Air-Marshal monitoring you activity :robot: ",
                                          colour=0x319f6b)
                        sys_embed.add_field(name='__Notice!__',
                                            value=text)

                        try:
                            await member.send(embed=sys_embed)
                        except Exception:
                            print(
                                Fore.RED + f"Message with instructions could not be delivered to {member} with "
                                           f"ID: {member.id} due to no DM rule")
                            pass
                    else:
                        print(
                            Fore.RED + f"Role Visitor does not exist on guild {member.guild} with id {member.guild.id}")

                        # Nothing to do as it is not registered
                elif sec_value == 2:
                    print(Fore.LIGHTWHITE_EX + f'Community {member.guild} not registered for the service')

            else:
                print(Fore.LIGHTWHITE_EX + f'{member} is BOT who joined {member.guild} with ID {member.guild.id}')
        else:
            print(f'Community {member.guild} not registered for spam prevention service')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """
        Clean up process once member leaves the guild

        Args:
            member ([type]): [description]
        """
        print(Fore.LIGHTYELLOW_EX + f'{member} left {member.guild}...')
        print(Fore.LIGHTWHITE_EX + f'Initiating clean up process for member {member} with ID {member.id}')
        jail_manager.clear_community_member_jail(community_id=member.guild.id, member_id=member.id)
        print(Fore.GREEN + f'Cleaning process finished')
        print(f'==============DONE=================')

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """
        Triggering message to system channel when bot joins new guild

        Args:
            guild ([discord.Guild])
        """
        print(Fore.LIGHTMAGENTA_EX + f'{self.bot.user} joined {guild} ')

        new_guild = Embed(title='__NEW GUILD!!!!__',
                          description=f'{self.bot.user} has joined new guild',
                          colour=Colour.green())
        new_guild.add_field(name='Guild name and id:',
                            value=f'{guild} {guild.id}',
                            inline=False)
        new_guild.add_field(name='Guild created:',
                            value=f'{guild.created_at}',
                            inline=False)
        new_guild.add_field(name='Guild Owner:',
                            value=f'{guild.owner} {guild.owner_id}',
                            inline=False)
        new_guild.add_field(name='Member Count',
                            value=f'{len(guild.members)} ({guild.member_count})',
                            inline=False)

        support_channels = bot_setup['supportChannel']
        for chn in support_channels:
            separator = ' '
            for user in chn['userTags']:
                usr = await self.bot.fetch_user(user_id=user)
                separator += usr.mention + " "

            dest = self.bot.get_channel(id=int(chn["channel"]))
            await dest.send(embed=new_guild, content=separator)
            guilds = await self.bot.fetch_guilds(limit=150).flatten()
            reach = len(self.bot.users)

            glob = Embed(title=f'{self.bot.user} Current Global Stats')
            glob.add_field(name='Guild Count',
                           value=f'{len(guilds)}',
                           inline=False)
            glob.add_field(name='Member Reach',
                           value=f"{reach}",
                           inline=False)
            await dest.send(embed=new_guild, content=separator)
            await dest.send(embed=glob)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        """
        Triggered when bot is removed from guild and system message is sent to channel on removal

        Args:
            guild (discord.Guild): [description]
        """
        print(Fore.LIGHTMAGENTA_EX + f'{self.bot.user} left {guild} ')
        dest = self.bot.get_channel(id=int(722048385078788217))
        new_guild = Embed(title='__REMOVED!!!!__',
                          description=f'{self.bot.user} has been removed',
                          colour=Colour.red())
        new_guild.add_field(name='Guild name and id:',
                            value=f'{guild} {guild.id}',
                            inline=False)
        new_guild.add_field(name='Guild created:',
                            value=f'{guild.created_at}',
                            inline=False)
        new_guild.add_field(name='Guild Owner:',
                            value=f'{guild.owner} {guild.owner_id}',
                            inline=False)
        new_guild.add_field(name='Member Count',
                            value=f'{len(guild.members)} ({guild.member_count})',
                            inline=False)
        new_guild.add_field(name='Premium Subscribers',
                            value=f'{guild.premium_subscription_count}',
                            inline=False)
        await dest.send(embed=new_guild)

        print(Fore.LIGHTWHITE_EX + f'Initiating clean up process for {guild} with ID {guild.id}')
        sup_sys_mng.remove_from_support_system(community_id=int(guild.id))
        spam_sys_mng.remove_from_spam_system(community_id=int(guild.id))
        jail_sys_mng.remove_from_jail_system(community_id=int(guild.id))
        jail_manager.clear_community_jail(community_id=int(guild.id))

        support_channels = bot_setup['supportChannel']
        for chn in support_channels:
            separator = ' '
            for user in chn['userTags']:
                usr = await self.bot.fetch_user(user_id=user)
                separator += usr.mention + "  "

            dest = self.bot.get_channel(id=int(chn["channel"]))
            guilds = await self.bot.fetch_guilds(limit=150).flatten()
            reach = len(self.bot.users)

            glob = Embed(title=f'{self.bot.user} Current Global Stats')
            glob.add_field(name='Guild Count',
                           value=f'{len(guilds)}',
                           inline=False)
            glob.add_field(name='Member Reach',
                           value=f"{reach}",
                           inline=False)
            await dest.send(embed=new_guild, content=separator)
            await dest.send(embed=glob)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, guild):
        """
        Function called when guild deletes channel

        Args:
            guild ([discord.Guild]): 
        """
        pass

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        """
        Function called when guild deletes role

        Args:
            role (discord.Role):
        """
        print('Gets called when guild removes role')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        """
        Function triggered when reaction is added to the mssage. Part of VAM spam prevention system

        Args:
            reaction ([type]): [description]
        """

        author = reaction.member  # Author of reaction
        guild_id = reaction.member.guild.id  # Guild of reaction
        if spam_sys_mng.check_if_security_activated(community_id=guild_id) == 1:
            details = spam_sys_mng.get_details_of_channel(community_id=reaction.member.guild.id)
            if details:
                if reaction.channel_id == details['appliedChannelId']:
                    if reaction.message_id == details['appliedMessageId']:
                        if reaction.emoji.name == '\U0001F44D':
                            role = utils.get(reaction.member.guild.roles, name='Visitor')
                            if role:
                                await reaction.member.add_roles(role)
                                print(Fore.YELLOW + f"Role Visitor given to the user {author} with ID: {author.id}")

                                text = f'Hey and welcome to the {author.guild}. ' \
                                       f'You have successfully verified yourself. Server channels have been opened up' \
                                       f' for you.Enjoy Your Stay!'

                                sys_embed = Embed(title=":rocket: __Air Marshal System Message__ :rocket:",
                                                  description=f"Access to {author.guild} granted!",
                                                  colour=0x319f6b)
                                sys_embed.add_field(name='__Notice!__',
                                                    value=text)

                                try:
                                    await author.send(embed=sys_embed)
                                except Exception:
                                    print(
                                        Fore.RED + f"Welcome message could not be delivered to {author} with "
                                                   f"ID: {author.id} due to no DM rule")
                                    pass

                                print(Fore.CYAN + f"Removing the Unverified role from {author} (ID: {author.id}")
                                role_rmw = utils.get(author.guild.roles, name="Unverified")
                                await author.remove_roles(role_rmw, reason='User accepted TOS')
                                print(Fore.YELLOW + f"Role Unverified removed from user {author} with ID: {author.id}")
                                print(Fore.GREEN + f"User accepted TOS {author} (ID: {author.id}")
                            else:
                                print(
                                    Fore.RED + f"Role Visitor does not exist on guild {author.guild} with id {author.guild.id}")
                        else:
                            message = 'You have either reacted with wrong emoji or than you did not want to accept ' \
                                      'Terms Of Service. Community has therefore stayed locked for you.'
                            title = f"Access to {reaction.guild} forbidden"
                            sys_embed = Embed(title="System Message",
                                              description=title,
                                              colour=0x319f6b)
                            sys_embed.add_field(name='Message',
                                                value=message)
                    else:
                        message = f'You have reacted to wrong message! Message ID is {details["appliedMessageId"]}!'
                        title = f":octagonal_sign:  __Air Marshal System Message__ :octagonal_sign: "
                        sys_embed = Embed(title="System Message",
                                          description=title,
                                          colour=0x319f6b)
                        sys_embed.add_field(name='Message',
                                            value=message)
                else:
                    pass
            else:
                pass
        else:
            pass

    @commands.Cog.listener()
    async def on_message(self, message):
        """

        Args:
            message (discord.Message):
        """

    @commands.Cog.listener()
    async def on_command(self, ctx):
        """
        global function activated everytime when command is executed
        """
        if isinstance(ctx.message.channel, TextChannel):
            try:
                await ctx.message.delete()
            except Exception as e:
                print(f'Bot could not delete command from channel: {e}')
                pass

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """
        Triggered everytime there is command error

        Args:
            ctx (discord.Context): [description]
            error (discord.Error): [description]
        """
        try:
            await ctx.message.delete()
        except Exception:
            pass
        if isinstance(error, commands.CommandNotFound):
            title = 'System Command Error'
            message = f':no_entry: Sorry, this command does not exist! Please' \
                      f'type `{bot_setup["command"]} help` to check available commands.'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                 sys_msg_title=title)
        elif isinstance(error, commands.BotMissingAnyRole):
            title = 'System Permission Error'
            message = f'Bot does not have sufficient rights to execute command '
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                 sys_msg_title=title)

        else:
            title = 'System Permission Error'
            message = f'Bot does not have sufficient rights to execute command: ```{error}``` '
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                 sys_msg_title=title)


def setup(bot):
    bot.add_cog(AutoFunctions(bot))
