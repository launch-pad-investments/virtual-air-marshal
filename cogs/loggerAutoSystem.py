import os
import sys
import time
from datetime import datetime, timedelta

import discord
from better_profanity import profanity
from colorama import Fore, init
from discord import DMChannel, Embed, Colour
from discord.ext import commands

from cogs.toolsCog.systemMessages import CustomMessages
from utils.jsonReader import Helpers
from backoffice.loggerSystemDb import LoggerSystem

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

init(autoreset=True)

helper = Helpers()
custom_messages = CustomMessages()
logger = LoggerSystem()

bot_setup = helper.read_json_file(file_name='mainBotConfig.json')


class LoggerAutoSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def check_logger_status(self, guild_id: int):
        """
        Check Logger Status on bot
        """
        if logger.check_community_reg_status(community_id=guild_id):
            if logger.check_logger_system_status(community_id=guild_id):
                return True
            else:
                return False
        else:
            return False

    def get_direction_color(self, direction: int):
        if direction == 0:
            # If someone leaves or bad happens
            return Colour.red()
        elif direction == 1:
            # If someone joins and good happens
            return Colour.green()
        elif direction == 2:
            return Colour.orange()
        
    async def send_member_join_message(self, channel_id, member: discord.Member, direction: int):

        col = self.get_direction_color(direction=direction)

        # Member properties

        display_name = member.display_name
        joined_at = member.joined_at
        avatar_url = member.avatar_url
        is_bot = member.bot
        mention = member.mention

        destination = self.bot.get_channel(id=channel_id)
        embed = Embed(title=f'User joined')

        pass

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        Send log when member joins
        """
        if self.check_logger_status(guild_id=member.guild.id):
            channel_id = logger.get_channel(community_id=member.guild.id)
            await self.send_member_join_message(channel_id=channel_id, member=member,direction=1)
        else:
            pass

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if self.check_logger_status(guild_id=member.guild.id):
            channel_id = logger.get_channel(community_id=member.guild.id)
            await self.send_log_message(channel_id=channel_id, member=member)
        else:
            pass

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

        Args:
            message (discord.Message): 
        """
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
            pass


def setup(bot):
    bot.add_cog(LoggerAutoSystem(bot))
