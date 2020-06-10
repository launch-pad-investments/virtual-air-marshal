
"""
COG: Handles the settings for communities verification system from bot invasion
"""

import os
import sys

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

from datetime import datetime
from datetime import timedelta
import time
from backoffice.communityProfilesDb import CommunityManager
import discord
from discord import Member as DiscordMember
from discord.ext import commands
from discord.ext.commands import Greedy
from jailList import JailManagement
from utils.jsonReader import Helpers
from cogs.toolsCog.systemMessages import CustomMessages
from colorama import Fore

helper = Helpers()
community_manager = CommunityManager()
jail_manager = JailManagement()
custom_message = CustomMessages()
bot_setup = helper.read_json_file(file_name='mainBotConfig.json')

def is_community_registered(ctx):
    return community_manager.check_community_reg_status(community_id=ctx.message.guild.id)

def is_community_not_registered(ctx):
    return community_manager.check_if_not_registered(community_id=ctx.message.guild.id)

def is_public(ctx):
    return ctx.message.channel.type != discord.ChannelType.private

def is_overwatch(ctx):
    access_list = [455916314238648340, 360367188432912385]
    return [member for member in access_list if member == ctx.message.author.id]

def is_community_owner(ctx):
    return ctx.message.author.id == ctx.message.guild.owner_id



class SpamService(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.check_any(commands.check(is_overwatch), commands.check(is_community_owner))
    @commands.check(is_community_registered)
    async def spam(self, ctx):
        try:
            await ctx.message.delete()
        except Exception:
            pass
        if ctx.invoked_subcommand is None:
            title = '__Available commands under ***Spam*** category!'
            description = 'Spam system has been designed witht he reason to protect community from invasion of spam bots. It includes '
            'Auto role uppon successfull reaction from the user to appropriate channel. '
            value = [{'name': f'MUST READ Before start',
                      'value': "Create two roles with exact name as written here:\n ***Unverified*** -> Given when member joins\n ***Visitor*** --> Given when member reacts appropriatelly"},
                     {'name': f'{bot_setup["command"]}spam on/off',
                      'value': 'This will turn the spam protection ON/OFF. In order to make it work you need to set appropriate message, channel,'
                      ' and role on community.'},
                     {'name': f'{bot_setup["command"]}spam set_channel <#discord.Channel>',
                      'value': "This will set the channel where bot will be listening for message and reaction."},
                     {'name': f'{bot_setup["command"]}spam set_message <Message ID as number>',
                      'value': "Right click on the messsage and copy its ID and provide it to bot. Message needs to be located in selected channel"}
                     ]

            await custom_message.embed_builder(ctx=ctx, title=title, description=description, data=value)    
    
    
    @spam.command()
    async def on(self,ctx):
        try:
            await ctx.message.delete()
        except Exception:
            pass
        if community_manager.check_welcome_channel_status(community_id=int(ctx.message.guild.id)):
            if community_manager.check_reaction_message_status(community_id=int(ctx.message.guild.id)):
                if community_manager.turn_on_off(community_id=int(ctx.message.guild.id),direction=1,service_type=2):
                    title='__System Message__'
                    message = 'You have turned ON the bot invasion prevention function successfully. '
                    await custom_message.system_message(ctx=ctx, color_code=0, message = message, destination = 1, sys_msg_title=title)
                else:
                    message = f'There was a backend error. Please try again later or contact one of the administrators on the community. We apologize for inconvinience'
                    await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
            else:
                message = f'You can not turn this service ON since the message where system will be listening for reacions, has not been provided yet. Please use first command {bot_setup["command"]}spam set_message <message id as INT> ***' 
                await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        else:
            message = f'You can not turn this service ON since the channel where system will be listening for reacions, has not been provided yet. Please use first command {bot_setup["command"]}spam set_channel <#discord.TextChannel> ***' 
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
    
    
    @spam.command()
    async def off(self,ctx):
        try:
            await ctx.message.delete()
        except Exception:
            pass
        if community_manager.turn_on_off(community_id=int(ctx.message.guild.id),direction=0,service_type=2):
                title='__System Message__'
                message = 'You have turned OFF the bot invasion prevention function successfully. Have in mind that now everything will needd to be done manually.'
                await custom_message.system_message(ctx=ctx, color_code=0, message = message, destination = 1, sys_msg_title=title)
        else:
            message = f'There was a backend error. Please try again later or contact one of the administrators on the community. We apologize for inconvinience'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)

    
    @spam.command()
    async def set_channel(self,ctx, channel:discord.TextChannel):
        try:
            await ctx.message.delete()
        except Exception:
            pass
        if community_manager.modify_channel(community_id=int(ctx.message.guild.id),channel_id=channel.id,channel_name=f'{channel.name}'):
            title='__System Message__'
            message = f'You have successfully set channel {channel} with id {channel.id} to listen for user verifications. Proceed with command ***{bot_setup["command"]} spam set_message <message ID> *** to identify message where user needs to react with :thumbs-up:'
            await custom_message.system_message(ctx=ctx, color_code=0, message = message, destination = 1, sys_msg_title=title)
        else:
            message = f'There was an issue while setting up channel to listen for user verifications. Please try again later' 
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
            
    
    @spam.command()
    async def set_message(self, ctx, message_id:int):
        try:
            await ctx.message.delete()
        except Exception:
            pass
        channel_db = community_manager.get_communtiy_settings(community_id=ctx.message.guild.id)
        if channel_db['appliedChannelId']:
            channel = self.bot.get_channel(id=int(channel_db['appliedChannelId']))
            msg = await channel.fetch_message(int(message_id))
            if msg is not None:
                if msg.guild.id == ctx.message.guild.id:
                    if community_manager.modify_message(community_id=ctx.message.guild.id,message_id=int(message_id)):
                        title='__System Message__'
                        message = f'You have set message to be listening for reaction successfully! Here is location of message:\n Location: #{msg.channel}\n ID: {msg.id}. \nProceed with final step by activating the service with ***{bot_setup["command"]} spam on***. '
                        await custom_message.system_message(ctx=ctx, color_code=0, message = message, destination = 1, sys_msg_title=title)
                else:
                    message = f'Why would you select message from different discord community. It does not make any sense'
                    await custom_message.system_message(ctx, message=message, color_code=1, destination=1)    
            else:
                message = f'Message could not be found on the community. Are you sure you have provided the right message ID?'
                await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        else:
            message = f'You need to first set channel with command {bot_setup["command"]} spam set_channel <#discord.TextChannel> *** before you can set the mssage from the selected channel.' 
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)

    @spam.error
    async def spam_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = f'You are either not an Overwatch member, owner of the community, or community has not been registered yet into the system. Use {bot_setup["command"]}service register to start'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        else:
            print(error)

def setup(bot):
    bot.add_cog(SpamService(bot))
