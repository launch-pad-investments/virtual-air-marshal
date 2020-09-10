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
from backoffice.loggerSystemDb import LoggerSystem
from utils.jsonReader import Helpers
from cogs.toolsCog.systemMessages import CustomMessages
from colorama import Fore
from cogs.toolsCog.checks import is_community_owner, is_overwatch, logger_registration_status, is_public, \
    admin_predicate

helper = Helpers()

logger = LoggerSystem()

custom_message = CustomMessages()
bot_setup = helper.read_json_file(file_name='mainBotConfig.json')


class LoggerService(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.check(is_public)
    @commands.check(logger_registration_status)
    @commands.bot_has_guild_permissions(administrator=True, )
    @commands.check_any(commands.check(is_overwatch), commands.check(is_community_owner),
                        commands.check(admin_predicate))
    async def logger(self, ctx):
        """
        Entry point for logger actions.

        Args:
            ctx (discord.Context)
        """
        # TODO rewrite command map
        try:
            await ctx.message.delete()
        except Exception:
            pass
        if ctx.invoked_subcommand is None:
            title = '__Available commands under ***LOGGER*** category!__'
            description = 'Logger system monitors activity on guild and provides notifications on changes.'
            ' All roles are removed and given back once jail-time has expired.'
            value = [{'name': f'{bot_setup["command"]}logger on',
                      'value': "Turns the jail ON"},
                     {'name': f'{bot_setup["command"]}logger off',
                      'value': "Turns the jail system off"},
                     {'name': f'{bot_setup["command"]}logger set_channel <#discord_channel>',
                      'value': "Turns the jail system off"}
                     ]

            await custom_message.embed_builder(ctx=ctx, title=title, description=description, data=value)

    @logger.command()
    async def set_channel(self, ctx, channel: discord.TextChannel):
        try:
            await ctx.message.delete()
        except Exception:
            pass
        if logger.modify_channel(community_id=int(ctx.message.guild.id), channel_id=channel.id,
                                 channel_name=f'{channel.name}'):
            title = '__System Message__'
            message = f'You have successfully set channel {channel} with id {channel.id} to accept log reports from ' \
                      f' {self.bot.user}'
            await custom_message.system_message(ctx=ctx, color_code=0, message=message, destination=1,
                                                sys_msg_title=title)
        else:
            message = f'There was an issue while setting up channel to listen for logs'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)

    @logger.command()
    async def on(self, ctx):
        """
        Command turns the jail and profanity system ON

        Args:
            ctx (discord.Context)
        """
        try:
            await ctx.message.delete()
        except Exception:
            pass

        if logger.turn_on_off(community_id=int(ctx.message.guild.id), direction=1):
            title = '__System Message__'
            message = 'You have turned ON the logging system. '
            await custom_message.system_message(ctx=ctx, color_code=0, message=message, destination=1,
                                                sys_msg_title=title)
        else:
            message = f'There was a backend error. Please try again later or contact one' \
                      f' of the administrators on the community. We apologize for inconvenience'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)

    @logger.command()
    async def off(self, ctx):
        """
        Command turns the jail and profanity system OFF

        Args:
            ctx (discord.Context)
        """
        try:
            await ctx.message.delete()
        except Exception:
            pass

        if logger.turn_on_off(community_id=int(ctx.message.guild.id), direction=0):
            title = '__System Message__'
            message = 'You have turned OFF logging system'
            await custom_message.system_message(ctx=ctx, color_code=0, message=message, destination=1,
                                                sys_msg_title=title)
        else:
            message = f'There was a backend error. Please try again later or contact one of ' \
                      f'the administrators on the community. We apologize for inconvenience'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)

    @logger.error
    async def logger_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = f'Command is allowed to be executed only on the public channels of the {ctx.message.guild}' \
                      f' and community needs to be registered into the ***LOGGER*** system.'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        if isinstance(error, commands.CheckAnyFailure):
            message = f'In order to use jail on {ctx.guild} you either need to be on ***Overwatch roster, owern ' \
                      f'of the community or have administrator*** rights!.'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        elif isinstance(error, commands.BotMissingPermissions):
            message = 'Bot has insufficient permissions which are required to register for services. It requires at ' \
                      'least administrator privileges with message and role management permissions!'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)

    @on.error
    async def on_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = f'{ctx.guild} has not been registered yet for ***LOGGER*** service. Please start' \
                      f' with ***{self.bot.mention} service register jail***'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)

    @off.error
    async def off_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = f'{ctx.guild} has not been registered yet for ***LOGGER*** service. ' \
                      f'Please start with ***{bot_setup["command"]} service register jail***'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)


def setup(bot):
    bot.add_cog(LoggerService(bot))
