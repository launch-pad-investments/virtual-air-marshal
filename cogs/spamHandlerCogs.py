"""
COG: Handles the settings for communities verification system from bot invasion
"""

import os
import sys

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

from backoffice.spamSystemDb import SpamSystemManager
import discord
from discord.ext import commands
from utils.jsonReader import Helpers
from cogs.toolsCog.systemMessages import CustomMessages
from cogs.toolsCog.checks import is_overwatch, is_community_owner, is_public, is_spam_registered

helper = Helpers()
spam_sys_mng = SpamSystemManager()
custom_message = CustomMessages()
bot_setup = helper.read_json_file(file_name='mainBotConfig.json')


class SpamService(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.command = bot_setup["command"]

    @commands.group()
    @commands.check(is_public)
    @commands.check_any(commands.check(is_overwatch), commands.check(is_community_owner))
    @commands.check(is_spam_registered)
    async def spam(self, ctx):
        if ctx.invoked_subcommand is None:
            title = '__Available commands under ***Spam*** category!__'
            description = 'Spam system has been designed with the reason to protect community from ' \
                          'invasion of spam bots. It includes Auto role upon successful reaction from the user ' \
                          'to appropriate channel. '
            value = [{"name": ":exclamation: Read Manual First :exclamation: ",
                      "value": f'```{self.command} spam manual```'},
                     {'name': f'Set channel',
                      'value': f'```{self.command} spam set_channel <#discord.Channel>```'},
                     {'name': f'Set message ID for bot to monitor for reaction',
                      'value': f'```{self.command} spam set_message <Message ID as number>```'},
                     {'name': 'turn spam ON or OFF',
                      'value': f'```{self.command} spam on/off```'},
                     ]

            await custom_message.embed_builder(ctx=ctx, title=title, description=description, data=value)

    @spam.command()
    async def manual(self, ctx):
        title = ':information_source: Setup Procedure :information_source: '
        description = ''
        value = [{'name': f':one: Manually Create Required Roles :one:',
                  'value': "Create two roles with exact name as written here:\n ***Unverified*** -> "
                           "Given when member joins\n ***Visitor*** --> Given when member reacts appropriately"},
                 {'name': f':two: Set channel for bot to monitor for verifications :two:',
                  'value': f'```{self.command} spam set_channel <#discord.Channel>```'},
                 {'name': f':three: Set message ID for bot to monitor for reaction :three: ',
                  'value': f'```{self.command} spam set_message <Message ID as number>```'},
                 {'name': ':four: Turn the spam ON :four',
                  'value': f'```{self.command} spam on```'},
                 {'name': ':five: ***@everyone*** :five:',
                  'value': f'It is crucial that @everyone has no rights what so ever across community as '
                           f'spam bots utilize its functions to view users. Also ***Unverified*** Should have '
                           f'granted read-only, view message history and add-reaction rights only on the channel'
                           f' where it is expected for incoming members to provide reaction. ***Visitor*** role '
                           f'should be assigned to all other channels of the server where you want user to have'
                           f' access to once he/she is verified.'},
                 ]

        await custom_message.embed_builder(ctx=ctx, title=title, description=description, data=value)

    @spam.command()
    async def on(self, ctx):
        if spam_sys_mng.check_welcome_channel_status(community_id=int(ctx.message.guild.id)):
            if spam_sys_mng.check_reaction_message_status(community_id=int(ctx.message.guild.id)):
                if spam_sys_mng.turn_on_off(community_id=int(ctx.message.guild.id), direction=1):
                    title = '__System Message__'
                    message = 'You have turned ON the bot invasion prevention function successfully. '
                    await custom_message.system_message(ctx=ctx, color_code=0, message=message, destination=1,
                                                        sys_msg_title=title)
                else:
                    message = f'There was a backend error. Please try again later or contact one of the ' \
                              f'administrators on the community. We apologize for inconvinience'
                    await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
            else:
                message = f'You can not turn this service ON since the message where system will be listening ' \
                          f'for reacions, has not been provided yet. Please use first command {bot_setup["command"]}' \
                          f'spam set_message <message id as INT> ***'
                await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        else:
            message = f'You can not turn this service ON since the channel where system will be listening for ' \
                      f'reacions, has not been provided yet. Please use first command {bot_setup["command"]}spam ' \
                      f'set_channel <#discord.TextChannel> ***'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)

    @spam.command()
    async def off(self, ctx):
        if spam_sys_mng.turn_on_off(community_id=int(ctx.message.guild.id), direction=0):
            title = '__System Message__'
            message = 'You have turned OFF the bot invasion prevention function successfully. Have in ' \
                      'mind that now everything will needd to be done manually.'
            await custom_message.system_message(ctx=ctx, color_code=0, message=message,
                                                destination=1, sys_msg_title=title)
        else:
            message = f'There was a backend error. Please try again later or contact one of the administrators ' \
                      f'on the community. We apologize for inconvinience'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)

    @spam.command()
    async def set_channel(self, ctx, channel: discord.TextChannel):
        if spam_sys_mng.modify_channel(community_id=int(ctx.message.guild.id), channel_id=channel.id,
                                       channel_name=f'{channel.name}'):
            title = '__System Message__'
            message = f'You have successfully set channel {channel} with id {channel.id} to listen for user ' \
                      f'verifications. Proceed with command ***{bot_setup["command"]} spam set_message <message ID> ' \
                      f'*** to identify message where user needs to react with :thumbs-up:'
            await custom_message.system_message(ctx=ctx, color_code=0, message=message, destination=1,
                                                sys_msg_title=title)
        else:
            message = f'There was an issue while setting up channel to listen for user verifications. ' \
                      f'Please try again later'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)

    @spam.command()
    async def set_message(self, ctx, message_id: int):
        channel_db = spam_sys_mng.get_communtiy_settings(community_id=ctx.message.guild.id)
        if channel_db['appliedChannelId']:
            channel = self.bot.get_channel(id=int(channel_db['appliedChannelId']))
            msg = await channel.fetch_message(int(message_id))
            if msg is not None:
                if msg.guild.id == ctx.message.guild.id:
                    if spam_sys_mng.modify_message(community_id=ctx.message.guild.id, message_id=int(message_id)):
                        title = '__System Message__'
                        message = f'You have set message to be listening for reaction successfully! ' \
                                  f'Here is location of message:\n Location: #{msg.channel}\n ID: {msg.id}.' \
                                  f' \nProceed with final step by activating the service with ' \
                                  f'***{bot_setup["command"]} spam on***. '
                        await custom_message.system_message(ctx=ctx, color_code=0, message=message, destination=1,
                                                            sys_msg_title=title)
                else:
                    message = f'Why would you select message from different discord community. It does ' \
                              f'not make any sense'
                    await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
            else:
                message = f'Message could not be found on the community. Are you sure you have provided the right ' \
                          f'message ID?'
                await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        else:
            message = f'You need to first set channel with command {bot_setup["command"]} spam set_channel ' \
                      f'<#discord.TextChannel> *** before you can set the mssage from the selected channel.'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)

    @spam.error
    async def spam_error(self, ctx, error):
        if isinstance(error, commands.CheckAnyFailure):
            message = f'You are either not an Overwatch member, owner of the community, or community has not ' \
                      f'been registered yet into the system. Use {bot_setup["command"]}service register to start'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        elif isinstance(error, commands.CheckFailure):
            message = f'This command is allowed to be executed only on the public channels of the community ' \
                      f'or than it has not been registered yet into {self.bot.user} system.\n Error: {error}'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        else:
            title = '__:bug: Found__'
            message = f'Bug has been found while executing command and {self.bot.user} service team has been ' \
                      f'automatically notified. We apologize for inconvinience!'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1, sys_msg_title=title)
            dest = await self.bot.fetch_user(user_id=int(360367188432912385))
            await custom_message.bug_messages(ctx=ctx, error=error, destination=dest)


def setup(bot):
    bot.add_cog(SpamService(bot))
