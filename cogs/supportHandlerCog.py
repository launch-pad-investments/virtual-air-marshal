import os
import sys

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

from datetime import datetime
from datetime import timedelta
import time
from discord import Member as DiscordMember

from backoffice.supportSystemDb import SupportSystemManager
from discord import TextChannel, Embed, Colour
from discord.ext import commands
from discord.ext.commands import Greedy
from utils.jsonReader import Helpers
from cogs.toolsCog.systemMessages import CustomMessages
from colorama import Fore
from cogs.toolsCog.checks import is_community_owner, is_overwatch, is_public, is_support_registered, check_if_support_channel_registered

helper = Helpers()
sup_sys_mng = SupportSystemManager()
custom_message = CustomMessages()
bot_setup = helper.read_json_file(file_name='mainBotConfig.json')


class SupportService(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.group()
    @commands.check(is_public)
    @commands.bot_has_guild_permissions(administrator=True, manage_messages=True, manage_roles=True)
    @commands.check_any(commands.has_guild_permissions(administrator=True),commands.check(is_overwatch), commands.check(is_community_owner))
    async def support(self, ctx):
        if ctx.invoked_subcommand is None:
            title = '__Available commands under ***Support*** category!__'
            description = 'Support System was designed to allow community owners collection of support requests to one channel and respond to users. Bellow are availabale commands'
            value = [{'name': f'{bot_setup["command"]}support set_channel <discord channel>',
                      'value': "Sets the channel where requested support tickets will be sent"},
                     {'name': f'{bot_setup["command"]}support on',
                      'value': "Sets the support service ON"},
                     {'name': f'{bot_setup["command"]}support off ',
                      'value': "Sets support service off"}
                     ]

            await custom_message.embed_builder(ctx=ctx, title=title, description=description, data=value)
            
    @support.command()
    @commands.check(is_support_registered)
    async def set_channel(self, ctx, chn: TextChannel):
        if sup_sys_mng.modify_channel(community_id=ctx.message.guild.id,channel_id=int(chn.id),channel_name=f'{chn}'):
            info_embed= Embed(title='__Support System Message__',
                              description='You have successfully set channel to listen for ticket supports.',
                              colour=Colour.green())
            info_embed.set_thumbnail(url=self.bot.user.avatar_url)
            info_embed.add_field(name='Channel Name',
                                 value=f'{chn}',
                                 inline=False)
            info_embed.add_field(name='Channel ID',
                                 value=f'{chn.id}',
                                 inline=False)
            info_embed.add_field(name=':warning: Notice :warning: ',
                                 value='If you will delete channel which is assigned to listen for support messages, it wont work, and you will need to set different channel',
                                 inline=False)
            info_embed.add_field(name='How to create support ticket',
                                 value=f'commands ticket issue')
            await ctx.author.send(embed=info_embed)
        else:
            message = f'There has been system backend error. Please try again later! We apologize for inconvinience'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
            
    @support.command()
    @commands.check(is_support_registered)
    @commands.check(check_if_support_channel_registered)
    async def on(self, ctx):
        try:
            await ctx.message.delete()
        except Exception:
            pass
        
        if sup_sys_mng.turn_on_off(community_id=ctx.message.channel.id, direction = 1):
            title='__System Message__'
            message = f'You have turned ON support ticket service successfully. Members can now create ticket by executing command {bot_setup["command"]} ticket <message>'
            await custom_message.system_message(ctx=ctx, color_code=0, message = message, destination = 1, sys_msg_title=title)
        else:
            message = f'There has been system backend error while trying to turn support service ON. Please try again later! We apologize for inconvinience'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)     

    @support.command()
    @commands.check(is_support_registered)
    @commands.check(check_if_support_channel_registered)
    async def off(self, ctx):
        try:
            await ctx.message.delete()
        except Exception:
            pass
        
        if sup_sys_mng.turn_on_off(community_id=int(ctx.message.guild.id),direction=0):
                title='__System Message__'
                message = 'You have turned OFF automtic jail system and profanity successfully. Your members can get crazy'
                await custom_message.system_message(ctx=ctx, color_code=0, message = message, destination = 1, sys_msg_title=title)
        else:
            message = f'There was a backend error. Please try again later or contact one of the administrators on the community. We apologize for inconvinience'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
            
    @set_channel.error
    async def set_channel_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = f'You have not registered community yet into ***SUPPORT*** system. Please first execute ***{bot_setup["command"]}service register support***'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        elif isinstance(error,commands.MissingRequiredArgument):
            message = f'You did not provide all required arguments. Command structure is {bot_setup["command"]} support set_channel <#discord.TextChannel>.'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        elif isinstance(error,commands.BadArgument):
            message = f'You have provide wrong argument for channel part. Channel needs to be tagged with #chanelName and a Text Channel Type. Command structure is {bot_setup["command"]} support set_channel <#discord.TextChannel>.'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        else:
            title='__:bug: Found__'
            message = f'Bug has been found while executing command and {self.bot.user} service team has been automatically notified. We apologize for inconvinience!'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1,sys_msg_title=title)
            
            dest = await self.bot.fetch_user(user_id=int(360367188432912385))
            await custom_message.bug_messages(ctx=ctx,error=error,destination=dest)
        
            
    @on.error
    async def on_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = f'You either have not registered community for ***SUPPORT*** system --> execute {bot_setup["command"]}service register support\n or have not set destination where tickets wil be sent {bot_setup["command"]} support set_channel <#discord.TextChannel> '
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        else:
            title='__:bug: Found__'
            message = f'Bug has been found while executing command and {self.bot.user} service team has been automatically notified. We apologize for inconvinience!'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1,sys_msg_title=title)
            
            dest = await self.bot.fetch_user(user_id=int(360367188432912385))
            await custom_message.bug_messages(ctx=ctx,error=error,destination=dest)

    @off.error
    async def off_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = f'You either have not registered community for ***SUPPORT*** system --> execute {bot_setup["command"]}service register support\n or have not set destination where tickets wil be sent {bot_setup["command"]} support set_channel <#discord.TextChannel> '
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        else:
            title='__:bug: Found__'
            message = f'Bug has been found while executing command and {self.bot.user} service team has been automatically notified. We apologize for inconvinience!'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1,sys_msg_title=title)
            
            dest = await self.bot.fetch_user(user_id=int(360367188432912385))
            await custom_message.bug_messages(ctx=ctx,error=error,destination=dest)
    
def setup(bot):
    bot.add_cog(SupportService(bot))
