import os
import sys
import time
from datetime import datetime, timedelta

import discord
from better_profanity import profanity
from colorama import Fore, init
from discord import DMChannel, Embed, Colour
from discord.ext import commands

from backoffice.jailManagementDb import JailManagement
from backoffice.jailSystemDb import JailSystemManager
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

bot_setup = helper.read_json_file(file_name='mainBotConfig.json')
CONST_JAIL_DURATION = 5


class AutoFunctions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def guild_notify(self, member, direction: int):
        """
        Custom notifications to desired channel
        Args:
            member ([discord.Member]): [description]
            direction (int): [0 if leaves, 1 if joins]
        """

        # kavic tag
        kavic = await self.bot.fetch_user(user_id=int(455916314238648340))
        # animus = await self.bot.fetch_user(user_id=int(360367188432912385))
        info_channel = self.bot.get_channel(id=int(722048385078788217))

        await info_channel(content=f'{kavic.mention} :arrow_double_down: ')

        time_joined = datetime.utcnow()
        if direction == 0:
            embed_info = Embed(title=f'User left {member.guild}',
                               colour=Colour.orange())
        elif direction == 1:
            embed_info = Embed(title=f'New user Joined {member.guild}',
                               colour=Colour.orange())
        embed_info.add_field(name='Time:',
                             value=f'{time_joined}')
        embed_info.add_field(name='User details',
                             value=f'{member}\n{member.id}')
        embed_info.add_field(name='Bot?',
                             value=f'{member.bot}\n')
        embed_info.set_thumbnail(url=member.avatar_url)
        await info_channel(embed=embed_info)

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
        if member.guild.id == 667607865199951872:
            await self.guild_notify(member=member, direction=1)
        else:
            pass

        if spam_sys_mng.check_community_reg_status(community_id=member.guild.id):
            if not member.bot:
                sec_value = spam_sys_mng.check_if_security_activated(community_id=int(member.guild.id))
                details = spam_sys_mng.get_details_of_channel(
                    community_id=member.guild.id)  # Get details of channel as dict

                if sec_value == 1:
                    role = discord.utils.get(member.guild.roles,
                                             name="Unverified")  # Check if role can be found if not than None
                    if role:
                        await member.add_roles(role)  # Give member a role
                        # Console printoutn
                        print(Fore.BLUE + f"New user joined community: {member} (ID: {member.id})")
                        print(Fore.YELLOW + f"Role Unveriffied given to the user {member} with ID: {member.id}")
                        text = f'Hey and welcome to the {member.guild}. '
                        f'Head to channel #{details["appliedChannelName"]} '
                        f'(ID: {details["appliedChannelId"]}) and accept TOS/Rules of community!'

                        sys_embed = discord.Embed(title="__Air Marshal System Message__",
                                                  description="This is auto-message!",
                                                  colour=0x319f6b)
                        sys_embed.add_field(name='Message',
                                            value=text,
                                            inline=False)
                        sys_embed.set_thumbnail(url=self.bot.user.avatar_url)
                        sys_embed.set_footer(text='Service provided by Launch Pad Investments')

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
                    role = discord.utils.get(member.guild.roles, name='Visitor')

                    if role:
                        await member.add_roles(role)

                        print(Fore.YELLOW + f"Role Visitor given to the user {member} with ID: {member.id}")
                        text = f'Hey and welcome to the {member.guild}. '
                        f'Head to channel #{details["appliedChannelName"]} '
                        f'(ID: {details["appliedChannelId"]}) and familiarize yourself with TOS/Rules of ' \
                        f'community and enjoy jour stay!'

                        sys_embed = discord.Embed(title=":rocket: __Air Marshal System Message__ :rocket:",
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

                        sys_embed = discord.Embed(title=":rocket: __Air Marshal System Message__ :rocket:",
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
        if member.guild.id == 667607865199951872:
            await self.guild_notify(member=member, direction=0)
        else:
            pass

        print(Fore.LIGHTWHITE_EX + f'Initiating clean up process for member {member} with ID {member.id}')
        jail_manager.clear_community_member_counter(community_id=member.guild.id, member_id=member.id)
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
            print(chn['userTags'])
            separator = ' '
            for user in chn['userTags']:
                usr = await self.bot.fetch_user(user_id=user)
                print(usr.mention)
                separator += usr.mention + " "
            print(separator)

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
        jail_manager.clear_community_counter(community_id=int(guild.id))
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
        print('Guild has deleted channel')

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
                            role = discord.utils.get(reaction.member.guild.roles, name='Visitor')
                            if role:
                                await reaction.member.add_roles(role)
                                print(Fore.YELLOW + f"Role Visitor given to the user {author} with ID: {author.id}")

                                text = f'Hey and welcome to the {author.guild}. '
                                f'You have successfully verified yourself, and gave yourself a chance to look' \
                                f' through its content. Enjoy Your Stay!'

                                sys_embed = discord.Embed(title=":rocket: __Air Marshal System Message__ :rocket:",
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

                                text = f'{author.guild} uses {self.bot.user} which is a product of Launch Pad ' \
                                       f'Investment Discord Group. '
                                f' It has been designed with the reason to allow moderation of the community.'

                                sys_embed = discord.Embed(title=":rocket: __Air Marshal System Message__ :rocket:",
                                                          description=f"Air-Marshal monitoring you activity :robot: ",
                                                          colour=0x319f6b)
                                sys_embed.add_field(name='__Notice!__',
                                                    value=text)

                                try:
                                    await author.send(embed=sys_embed)
                                except Exception:
                                    print(
                                        Fore.RED + f"Welcome message could not be delivered to {author} with ID: {author.id} due to no DM rule")
                                    pass

                                print(Fore.CYAN + f"Removing the Unverified role from {author} (ID: {author.id}")
                                role_rmw = discord.utils.get(author.guild.roles, name="Unverified")
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
                            sys_embed = discord.Embed(title="System Message",
                                                      description=title,
                                                      colour=0x319f6b)
                            sys_embed.add_field(name='Message',
                                                value=message)
                    else:
                        message = f'You have reacted to wrong message! Message ID is {details["appliedMessageId"]}!'
                        title = f":octagonal_sign:  __Air Marshal System Message__ :octagonal_sign: "
                        sys_embed = discord.Embed(title="System Message",
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
        Function called everytime a message is sent on channel. Used for profanity system and jail management

        Args:
            message (discord.Message): 
        """
        if not message.author.bot:
            if not isinstance(message.channel, DMChannel):
                user_id = message.author.id
                

                if message.author.id != message.guild.owner_id:
                    if jail_sys_mng.jail_activated(
                            community_id=message.guild.id):  # Check if community has jail activated
                        if message.author.id != message.guild.owner_id:
                            if profanity.contains_profanity(message.content):
                                await message.delete()
                                await message.channel.send(
                                    f'{message.author.mention} You cant use bad words on {message.guild}!',
                                    delete_after=15)
                                if not jail_manager.check_if_in_jail(user_id=int(user_id)):  # If user is not jailed yet
                                    if jail_manager.check_if_in_counter(discord_id=user_id):
                                        current_score = jail_manager.increase_count(discord_id=user_id)
                                        if current_score >= 3:
                                            print(Fore.GREEN + 'Someone needs to be jailed')
                                            # Current time
                                            start = datetime.utcnow()
                                            print(Fore.GREEN + f'@{start}')
                                            # Set the jail expiration to after N minutes
                                            td = timedelta(minutes=int(CONST_JAIL_DURATION))

                                            # calculate future date
                                            end = start + td
                                            expiry = (int(time.mktime(end.timetuple())))
                                            end_date_time_stamp = datetime.utcfromtimestamp(expiry)

                                            # guild = self.bot.get_guild(id=int(message.guild.id))  # Get guild
                                            active_roles = [role.id for role in message.author.roles][
                                                        1:]  # Get active roles
                                            print(Fore.GREEN + f'Has roles:')
                                            for r in active_roles:
                                                print(Fore.YELLOW + f'@Role: {r}')

                                            # jail user in database
                                            if jail_manager.throw_to_jail(user_id=message.author.id,
                                                                        community_id=message.guild.id,
                                                                        expiration=expiry, role_ids=active_roles):
                                                # Remove user from active counter database
                                                if jail_manager.remove_from_counter(discord_id=int(user_id)):

                                                    # Send message
                                                    jailed_info = discord.Embed(title='__You have been jailed!__',
                                                                                description=f' You have been automatically jailed, since you have broken the'
                                                                                            f'communication rules on community {message.guild} 3 times in a row. Next time be more cautious'
                                                                                            f' on how you communicate. Status will be restored once Jail Time Expires.',
                                                                                color=discord.Color.red())
                                                    jailed_info.add_field(name=f'Jail time duration:',
                                                                        value=f'{CONST_JAIL_DURATION} minutes',
                                                                        inline=False)
                                                    jailed_info.add_field(name=f'Sentence started @:',
                                                                        value=f'{start} UTC',
                                                                        inline=False)
                                                    jailed_info.add_field(name=f'Sentece ends on:',
                                                                        value=f'{end_date_time_stamp} UTC',
                                                                        inline=False)
                                                    jailed_info.set_thumbnail(url=self.bot.user.avatar_url)
                                                    await message.author.send(embed=jailed_info)
                                                    await message.channel.send(content=':cop:', delete_after=60)

                                                    # Jailing time

                                                    # ADD Jailed role to user
                                                    print(Fore.GREEN + 'Getting Jailed role on community')
                                                    role = discord.utils.get(message.guild.roles, name="Jailed")
                                                    await message.author.add_roles(role, reason='Jailed......')
                                                    print(Fore.RED + f'User {message.author} has been jailed!!!!')

                                                    print(Fore.GREEN + 'Removing active roles from user')
                                                    for role in active_roles:
                                                        role = message.guild.get_role(role_id=int(role))  # Get the role
                                                        await message.author.remove_roles(role,
                                                                                        reason='Jail time served')
                                        else:
                                            await message.channel.send(
                                                content=f'{message.author.mention} You have received your {current_score}. strike. When you reach 3...you will be jailed for {CONST_JAIL_DURATION}!',
                                                delete_after=10)
                                    else:
                                        jail_manager.apply_user(discord_id=user_id)
                                        await message.channel.send(
                                            content='You have received your first strike. once you reach 3...you '
                                                    'will be spanked and thrown to jail where only Animus can save you',
                                            delete_after=50)
                                        await message.delete()
                                else:
                                    pass
                            else:
                                pass
                        else:
                            pass
                    else:
                        pass
                else:
                    pass

                        
            else:
                print('Someone wanted to jail over DM')
        else:
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


def setup(bot):
    bot.add_cog(AutoFunctions(bot))
