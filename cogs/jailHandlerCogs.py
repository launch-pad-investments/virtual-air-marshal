import os
import sys

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

from datetime import datetime
from datetime import timedelta
import time
import discord
from discord import Member as DiscordMember
from backoffice.jailSystemDb import JailSystemManager
from discord.ext import commands
from discord.ext.commands import Greedy
from jailList import JailManagement
from utils.jsonReader import Helpers
from cogs.toolsCog.systemMessages import CustomMessages
from colorama import Fore

helper = Helpers()
jail_sys_manager = JailSystemManager()
jail_manager = JailManagement()
custom_message = CustomMessages()
bot_setup = helper.read_json_file(file_name='mainBotConfig.json')

def is_community_registered(ctx):
    return jail_sys_manager.check_if_jail_registered(community_id=ctx.message.guild.id)

def is_community_not_registered(ctx):
    return jail_sys_manager.check_if_jail_not_registered(community_id=ctx.message.guild.id)

def is_public(ctx):
    return ctx.message.channel.type != discord.ChannelType.private

def is_overwatch(ctx):
    access_list = bot_setup['userAccess']
    return [user for user in access_list if ctx.message.author.id == int(user)]

def is_community_owner(ctx):
    return ctx.message.author.id == ctx.message.guild.owner_id

class JailService(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.group()
    @commands.check_any(commands.check(is_overwatch), commands.check(is_community_owner), commands.check(is_community_registered))
    async def jail(self, ctx):
        if ctx.invoked_subcommand is None:
            title = '__Available commands under ***Jail*** category!'
            description = 'Jail system was designed with intentions to keep the language of the community clean and social. If member breaches language for 3 minutes, he/she is sent to jail for 2 minutes.' 
            ' All roles are removed and given back once jail-time has expired.'
            value = [{'name': f'{bot_setup["command"]}jail set <>',
                      'value': "Auto language moderation category of settings for community with auto jail and release function"},
                     ]

            await custom_message.embed_builder(ctx=ctx, title=title, description=description, data=value)
            
            
    @spam.command()
    async def on(self,ctx):
        try:
            await ctx.message.delete()
        except Exception:
            pass
        if jail_sys_manager.check_welcome_channel_status(community_id=int(ctx.message.guild.id)):
            if jail_sys_manager.check_reaction_message_status(community_id=int(ctx.message.guild.id)):
                if jail_sys_manager.turn_on_off(community_id=int(ctx.message.guild.id),direction=1):
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
        if spam_sys_mng.turn_on_off(community_id=int(ctx.message.guild.id),direction=0):
                title='__System Message__'
                message = 'You have turned OFF the bot invasion prevention function successfully. Have in mind that now everything will needd to be done manually.'
                await custom_message.system_message(ctx=ctx, color_code=0, message = message, destination = 1, sys_msg_title=title)
        else:
            message = f'There was a backend error. Please try again later or contact one of the administrators on the community. We apologize for inconvinience'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)

    
            
def setup(bot):
    bot.add_cog(JailService(bot))
