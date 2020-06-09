
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
customMessages = CustomMessages()
bot_setup = helper.read_json_file(file_name='mainBotConfig.json')

def is_community_registered(ctx):
    return community_manager.check_community_reg_status(community_id=ctx.message.guild.id)

def is_community_not_registered(ctx):
    return community_manager.check_if_not_registered(community_id=ctx.message.guild.id)

def is_public(ctx):
    return ctx.message.channel.type != discord.ChannelType.private

def is_overwatch(ctx):
    access_list = bot_setup['userAccess']
    return [user for user in access_list if ctx.message.author.id == int(user)]

def is_community_owner(ctx):
    return ctx.message.author.id == ctx.message.guild.owner_id



class SpamService(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @service.group()
    @commands.check(is_overwatch)
    @commands.check(is_community_owner)
    @commands.check(is_community_registered)
    async def spam(self, ctx):
        if ctx.invoked_subcommand is None:
            title = '__Available commands under ***Spam*** category!'
            description = 'Spam system has been designed witht he reason to protect community from invasion of spam bots. It includes '
            'Auto role uppon successfull reaction from the user to appropriate channel. '
            value = [{'name': f'MUST READ Before start',
                      'value': "Create two roles with exact name as written here:\n ***Unverified*** -> Given when member joins\n ***Visitor*** --> Given when member reacts appropriatelly"},
                     {'name': f'{bot_setup["command"]}spam turn <ON/OFF>',
                      'value': 'This will turn the spam protection ON/OFF. In order to make it work you need to set appropriate message, channel,'
                      ' and role on community.'},
                     {'name': f'{bot_setup["command"]}spam set_channel <#discord.Channel>',
                      'value': "This will set the channel where bot will be listening for message and reaction."},
                     {'name': f'{bot_setup["command"]}spam set_message <Message ID as number>',
                      'value': "Right click on the messsage and copy its ID and provide it to bot. Message needs to be located in selected channel"}
                     ]

            await customMessages.embed_builder(ctx=ctx, title=title, description=description, data=value)    
    
    
    
        @spam.error
    async def spam_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = 'You are either not an Overwatch member, owner of the community, or community has not been registered yet into the system.'
            await customMessages.system_message(ctx, message=message, color_code=1, destination=1)
        else:
            print(error)

def setup(bot):
    bot.add_cog(SpamService(bot))
