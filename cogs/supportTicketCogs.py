
"""
COG: Handles the settings for communities verification system from bot invasion
"""

import os
import sys

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

from datetime import datetime
from datetime import timedelta
from uuid import uuid4
import time

from discord.ext import commands
from discord import Colour, Embed


from utils.jsonReader import Helpers
from backoffice.supportSystemDb import SupportSystemManager
from cogs.toolsCog.systemMessages import CustomMessages
from cogs.toolsCog.checks import is_overwatch, is_community_owner, is_community_registered, is_public, is_text_channel, check_if_support_activated
from colorama import Fore

helper = Helpers()
support_sys_mng = SupportSystemManager()
custom_message = CustomMessages()
bot_setup = helper.read_json_file(file_name='mainBotConfig.json')

class SpamService(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def length_checker(self, message):
        print(len(message))
        if 20 < len(message) < 200:
            return True
        else:
            return False
        
    async def send_ticket_message_author(self, ctx, time_of_request,department,ticket_id,support_msg,colour):
        try:
            user_msg = Embed(title='__Support ticket issued successfully__',
                                description='Automatic System Message',
                                timestamp = time_of_request,
                                colour = Colour.green())
            user_msg.set_thumbnail(url=self.bot.user.avatar_url)

            user_msg.add_field(name='Sys message',
                                value=f'We would like to inform you that your support ticket has been recieved successfully. One of the ' 
                                f'support staff from {ctx.guild} will be in contact with you as soon as possible!',
                                inline= False)
            user_msg.add_field(name='Community:',
                                value=f'{ctx.message.guild}',
                                inline= False)
            user_msg.add_field(name='Department:',
                                value=f'{department}',
                                inline= False)
            user_msg.add_field(name="Reference Support Ticker Number",
                                value=ticket_id,
                                inline=False)
            user_msg.add_field(name="Reques message",
                                value=f'{support_msg}',
                                inline=False)               
            user_msg.set_footer(text='Service provided by Launch Pad Investments')
            await ctx.author.send(embed=user_msg)
            return True
        except Exception:
            return False
        
    async def send_ticket_message_channel(self, ctx, message, department:str, color_code:Colour, ticket_id:str, time_of_request):
        try:
            channel_id = int(support_sys_mng.get_channel(community_id=ctx.message.guild.id))
            dest = self.bot.get_channel(id=int(channel_id))

            time_of_request = datetime.utcnow()
            supp_msg = Embed(title='__Support requested__',
                            colour = Colour.magenta(),
                            timestamp=time_of_request)
            supp_msg.set_thumbnail(url=ctx.message.author.avatar_url)
            supp_msg.add_field(name="Department",
                            value=f'{department}',
                            inline=False)
            supp_msg.add_field(name="from",
                               value= f'{ctx.message.author} id: {ctx.message.author.id}',
                               inline=False)
            supp_msg.add_field(name="Ticket ID",
                                value=ticket_id,
                                inline=False)
            supp_msg.add_field(name="Message Content",
                            value=f'{message}',
                            inline=False)
            
            await dest.send(content=f"TICKET: {ticket_id}")
            support_msg = await dest.send(embed=supp_msg)
            await support_msg.add_reaction(emoji="⛔")
            
            return True
        except Exception:
            return False
        

    @commands.group()
    @commands.check(is_public)
    async def ticket(self, ctx):
        try:
            await ctx.message.delete()
        except Exception:
            pass
        if ctx.invoked_subcommand is None:
            title = '__Available commands for issuing a  ***Support*** ticket!'
            description = 'Ticket can be opened directly to the staff of the community. Bellow is representation of all available ticket types'
            value = [{'name': f'General inquiries department',
                      'value': f"{bot_setup['command']} ticket general <message>"},
                     {'name': f'Marketing department',
                      'value': f"{bot_setup['command']} ticket marketing <message>"},
                     {'name': f'Complaints department',
                      'value': f"{bot_setup['command']} ticket report <message>"}
                     ]

            await custom_message.embed_builder(ctx=ctx, title=title, description=description, data=value)    
    
    @ticket.command()
    @commands.check(is_public)
    async def marketing(self, ctx, *,message:str):
        if self.length_checker(message=message):
            ticket_no =  str(uuid4())
            time_of_request = datetime.utcnow()
            if support_sys_mng.check_if_support_activated(community_id=ctx.guild.id):
                if await self.send_ticket_message_channel(ctx=ctx,message=message, department='Marketing', color_code=Colour.magenta(), ticket_id=ticket_no,time_of_request = time_of_request):
                    if await self.send_ticket_message_author(ctx=ctx, time_of_request=time_of_request, department='Marketing',ticket_id=ticket_no,support_msg=message,colour=Colour.magenta()):
                        return
                    else:
                        title='__Support System Internal Error__'
                        message = f'System could deliver a copy of the ticket to your DM however support has recieved it and will be in touch as soon as possible. We apologize for inconvinience!'
                        await custom_message.system_message(ctx, message=message, color_code=1, destination=1, sys_msg_title=title)    
                else:
                    title='__Support System Internal Error__'
                    message = f'System could not process you request at this moment. Please try again later. We apologize for inconvinience!'
                    await custom_message.system_message(ctx, message=message, color_code=1, destination=1, sys_msg_title=title)     
            else:
                message = f'{ctx.guild} does not have activate support ticket service. Please contact administrators directly'
                await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        else:
            message = f'Message needs to be between 20 and 200 characters in length!'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
    
    @ticket.command()
    @commands.check(is_public)
    async def report(self, ctx, *, message:str):
        if self.length_checker(message=message):
            ticket_no =  str(uuid4())
            time_of_request = datetime.utcnow()
            if support_sys_mng.check_if_support_activated(community_id=ctx.guild.id):
                if await self.send_ticket_message_channel(ctx=ctx,message=message, department='Report', color_code=Colour.purple(),ticket_id=ticket_no, time_of_request = time_of_request):
                    if await self.send_ticket_message_author(ctx=ctx, time_of_request=time_of_request,department='Marketing',ticket_id=ticket_no,support_msg=message,colour=Colour.magenta()):
                        return
                    else:
                        title='__Support System Internal Error__'
                        message = f'System could deliver a copy of the ticket to your DM however support has recieved it and will be in touch as soon as possible. We apologize for inconvinience!'
                        await custom_message.system_message(ctx, message=message, color_code=1, destination=1, sys_msg_title=title)     
                else:
                    title='__Support System Internal Error__'
                    message = f'System could not process you request at this moment. Please try again later. We apologize for inconvinience!'
                    await custom_message.system_message(ctx, message=message, color_code=1, destination=1, sys_msg_title=title) 
            else:
                message = f'{ctx.guild} does not have activate support ticket service. Please contact administrators directly'
                await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        else:
            message = f'Message needs to be between 20 and 200 characters in length!'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
    
    @ticket.command()
    @commands.check(is_public)
    async def general(self, ctx, *, message:str):
        if self.length_checker(message=message):
            print('#1')
            ticket_no =  str(uuid4())
            time_of_request = datetime.utcnow()
            if support_sys_mng.check_if_support_activated(community_id=ctx.guild.id):
                print('#2')
                if await self.send_ticket_message_channel(ctx=ctx,message=message, department='General', color_code=Colour.orange(),ticket_id=ticket_no,time_of_request = time_of_request):
                    print('#3')
                    if await self.send_ticket_message_author(ctx=ctx, time_of_request=time_of_request,department='Marketing',ticket_id=ticket_no,support_msg=message,colour=Colour.magenta()):
                        return
                    else:
                        title='__Support System Internal Error__'
                        message = f'System could deliver a copy of the ticket to your DM however support has recieved it and will be in touch as soon as possible. We apologize for inconvinience!'
                        await custom_message.system_message(ctx, message=message, color_code=1, destination=1, sys_msg_title=title)    
                else:
                    title='__Support System Internal Error__'
                    message = f'System could not process you request at this moment. Please try again later. We apologize for inconvinience!'
                    await custom_message.system_message(ctx, message=message, color_code=1, destination=1, sys_msg_title=title)
            else:
                message = f'{ctx.guild} does not have activate support ticket service. Please contact administrators directly'
                await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        else:
            message = f'Message needs to be between 20 and 200 characters in length!'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)

    @marketing.error
    async def marketing_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            title='__Support System Check Error__'
            message = f'{error}'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1,sys_msg_title=title)
        elif isinstance(error, commands.MissingRequiredArgument):
            title='__Missing Required Argument__'
            message = f'You forgot to provide required argument: {error}'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1,sys_msg_title=title)
        else:
            title='__:bug: Found__'
            message = f'Bug has been found while executing command and {self.bot.user} service team has been automatically notified. We apologize for inconvinience!'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1,sys_msg_title=title)
            
            dest = await self.bot.fetch_user(user_id=int(360367188432912385))
            await custom_message.bug_messages(ctx=ctx,error=error,destination=dest)
            
    @general.error
    async def general_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            title='__Support System Check Error__'
            message = f'Support request needs to be issued on one of the Text Channel on community {ctx.guild}: {error}'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1,sys_msg_title=title)
        elif isinstance(error, commands.MissingRequiredArgument):
            title='__Missing Required Argument__'
            message = f'You forgot to provide required argument: {error}'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1,sys_msg_title=title)
        else:
            title='__:bug: Found__'
            message = f'Bug has been found while executing command and {self.bot.user} service team has been automatically notified. We apologize for inconvinience!'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1,sys_msg_title=title)
            
            dest = await self.bot.fetch_user(user_id=int(360367188432912385))
            await custom_message.bug_messages(ctx=ctx,error=error,destination=dest)

    @report.error
    async def report_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            title='__Support System Check Error__'
            message = f'Support request needs to be issued on one of the Text Channel on community {ctx.guild}: {error}'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1,sys_msg_title=title)
        elif isinstance(error, commands.MissingRequiredArgument):
            title='__Missing Required Argument__'
            message = f'You forgot to provide required argument: {error}'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1,sys_msg_title=title)
        else:
            title='__:bug: Found__'
            message = f'Bug has been found while executing command and {self.bot.user} service team has been automatically notified. We apologize for inconvinience!'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1,sys_msg_title=title)
            
            dest = await self.bot.fetch_user(user_id=int(360367188432912385))
            await custom_message.bug_messages(ctx=ctx,error=error,destination=dest)

    @ticket.error
    async def ticket_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            title='__Support System Check Error__'
            message = f'Support request needs to be issued on one of the public Text Channels on community {ctx.guild} and community needs to have support system activated: {error}'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1,sys_msg_title=title)

        else:
            title='__:bug: Found__'
            message = f'Bug has been found while executing command and {self.bot.user} service team has been automatically notified. We apologize for inconvinience!'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1,sys_msg_title=title)
            
            dest = await self.bot.fetch_user(user_id=int(360367188432912385))
            await custom_message.bug_messages(ctx=ctx,error=error,destination=dest)

def setup(bot):
    bot.add_cog(SpamService(bot))
