"""
COG: Contact with the Virtual Air Marshall Support staff
"""

import os
import sys

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

from datetime import datetime
from uuid import uuid4

from discord.ext import commands
from discord import Colour, Embed

from utils.jsonReader import Helpers
from backoffice.supportSystemDb import SupportSystemManager
from cogs.toolsCog.systemMessages import CustomMessages
from cogs.toolsCog.checks import is_public, is_community_owner

helper = Helpers()
support_sys_mng = SupportSystemManager()
custom_message = CustomMessages()
bot_setup = helper.read_json_file(file_name='mainBotConfig.json')


class StaffContactCmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = int(bot_setup["supportChannel"][0]["channel"])
        self.user_tags_list = bot_setup["supportChannel"][0]["userTags"]

    def length_checker(self, message):
        print(len(message))
        if 20 < len(message) < 200:
            return True
        else:
            return False

    async def send_ticket_message_author(self, ctx, time_of_request, department, ticket_id, support_msg, colour):
        try:
            user_msg = Embed(title='__Support ticket issued successfully__',
                             description='Automatic System Message',
                             timestamp=time_of_request,
                             colour=Colour.green())
            user_msg.set_thumbnail(url=self.bot.user.avatar_url)

            user_msg.add_field(name='Sys message',
                               value=f'We would like to inform you that your support ticket'
                                     f' has been received successfully. One of the '
                                     f'support staff  will be in contact with you as soon as possible!',
                               inline=False)
            user_msg.add_field(name='Community:',
                               value=f'{ctx.message.guild}',
                               inline=False)
            user_msg.add_field(name='Department:',
                               value=f'{department}',
                               inline=False)
            user_msg.add_field(name="Reference Support Ticker Number",
                               value=ticket_id,
                               inline=False)
            user_msg.add_field(name="Request message",
                               value=f'{support_msg}',
                               inline=False)
            user_msg.set_footer(text='Service provided by Launch Pad Investments')
            await ctx.author.send(embed=user_msg)
            return True
        except Exception:
            return False

    async def send_ticket_message_channel(self, ctx, message, department: str, ticket_id: str):

        mention_str = ''
        for u in self.user_tags_list:
            user = await self.bot.fetch_user(id=int(u))
            mention = user.mention
            mention_str += mention

        try:

            dest = self.bot.get_channel(id=int(self.channel_id))
            time_of_request = datetime.utcnow()
            supp_msg = Embed(title='__Support requested__',
                             colour=Colour.magenta(),
                             timestamp=time_of_request)
            supp_msg.set_thumbnail(url=ctx.message.author.avatar_url)
            supp_msg.add_field(name='From Guild',
                               value=f'{ctx.message.guild}')
            supp_msg.add_field(name="Subject",
                               value=f'{department}',
                               inline=False)
            supp_msg.add_field(name="From guild owner",
                               value=f'{ctx.message.author} id: {ctx.message.author.id}',
                               inline=False)
            supp_msg.add_field(name="Ticket ID",
                               value=ticket_id,
                               inline=False)
            supp_msg.add_field(name="Message Content",
                               value=f'{message}',
                               inline=False)
            await dest.send(content=f"{mention_str} TICKET: {ticket_id}")
            support_msg = await dest.send(embed=supp_msg)
            await support_msg.add_reaction(emoji="⛔")

            return True
        except Exception as e:
            print(e)
            return False

    @commands.group()
    @commands.check(is_public)
    @commands.check(is_community_owner)
    async def sys(self, ctx):
        if ctx.invoked_subcommand is None:
            title = '__Available commands for issuing a  ***Support*** ticket!'
            description = 'Message can be sent directly to Virtual Air Marshal development team and they will be in ' \
                          'touch ASAP.'
            value = [{'name': f'Feature request Message',
                      'value': f"{bot_setup['command']} sys feature <message>"},
                     {'name': f'Bug Report Message',
                      'value': f"{bot_setup['command']} sys bug <message>"},
                     {'name': f'Marketing inquiry',
                      'value': f"{bot_setup['command']} sys marketing <message>"},
                     {'name': f'Other messages',
                      'value': f"{bot_setup['command']} sys other <message>"}
                     ]

            await custom_message.embed_builder(ctx=ctx, title=title, description=description, data=value)

    @sys.command()
    @commands.check(is_public)
    async def feature(self, ctx, *, message: str):
        if self.length_checker(message=message):  # Message length checker
            ticket_no = str(uuid4())
            time_of_request = datetime.utcnow()

            if await self.send_ticket_message_channel(ctx=ctx, message=message, department='Feature',
                                                      ticket_id=ticket_no):
                if await self.send_ticket_message_author(ctx=ctx, time_of_request=time_of_request,
                                                         department='Feature', ticket_id=ticket_no,
                                                         support_msg=message, colour=Colour.magenta()):
                    return
                else:
                    title = '__Support System Internal Error__'
                    message = f'System could deliver a copy of the ticket to your DM however ' \
                              f'support has recieved it and will be in touch as soon as possible. We apologize ' \
                              f'for inconvinience!'
                    await custom_message.system_message(ctx, message=message, color_code=1, destination=1,
                                                        sys_msg_title=title)
            else:
                title = '__Support System Internal Error__'
                message = f'System could not process you request at this moment. Please try again later. ' \
                          f'We apologize for inconvenience!'
                await custom_message.system_message(ctx, message=message, color_code=1, destination=1,
                                                    sys_msg_title=title)
        else:
            message = f'Message needs to be between 20 and 200 characters in length!'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)

    @sys.command()
    @commands.check(is_public)
    async def bug(self, ctx, *, message: str):
        if self.length_checker(message=message):
            ticket_no = str(uuid4())
            time_of_request = datetime.utcnow()

            if await self.send_ticket_message_channel(ctx=ctx, message=message, department='Marketing',
                                                      ticket_id=ticket_no):
                if await self.send_ticket_message_author(ctx=ctx, time_of_request=time_of_request,
                                                         department='Feature', ticket_id=ticket_no,
                                                         support_msg=message, colour=Colour.magenta()):
                    return
                else:
                    title = '__Support System Internal Error__'
                    message = f'System could deliver a copy of the ticket to your DM however ' \
                              f'support has recieved it and will be in touch as soon as possible. We apologize ' \
                              f'for inconvinience!'
                    await custom_message.system_message(ctx, message=message, color_code=1, destination=1,
                                                        sys_msg_title=title)
            else:
                title = '__Support System Internal Error__'
                message = f'System could not process you request at this moment. Please try again later. ' \
                          f'We apologize for inconvinience!'
                await custom_message.system_message(ctx, message=message, color_code=1, destination=1,
                                                    sys_msg_title=title)

        else:
            message = f'Message needs to be between 20 and 200 characters in length!'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)

    @sys.command()
    @commands.check(is_public)
    async def marketing(self, ctx, *, message: str):
        if self.length_checker(message=message):
            ticket_no = str(uuid4())
            time_of_request = datetime.utcnow()

            if await self.send_ticket_message_channel(ctx=ctx, message=message, department='Marketing',
                                                      ticket_id=ticket_no):
                if await self.send_ticket_message_author(ctx=ctx, time_of_request=time_of_request,
                                                         department='Feature', ticket_id=ticket_no,
                                                         support_msg=message, colour=Colour.magenta()):
                    return
                else:
                    title = '__Support System Internal Error__'
                    message = f'System could deliver a copy of the ticket to your DM however ' \
                              f'support has recieved it and will be in touch as soon as possible. We apologize ' \
                              f'for inconvinience!'
                    await custom_message.system_message(ctx, message=message, color_code=1, destination=1,
                                                        sys_msg_title=title)
            else:
                title = '__Support System Internal Error__'
                message = f'System could not process you request at this moment. Please try again later. ' \
                          f'We apologize for inconvinience!'
                await custom_message.system_message(ctx, message=message, color_code=1, destination=1,
                                                    sys_msg_title=title)

        else:
            message = f'Message needs to be between 20 and 200 characters in length!'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)

    @sys.command()
    @commands.check(is_public)
    async def other(self, ctx, *, message: str):
        try:
            await ctx.message.delete()
        except Exception:
            pass
        if self.length_checker(message=message):
            ticket_no = str(uuid4())
            time_of_request = datetime.utcnow()

            if await self.send_ticket_message_channel(ctx=ctx, message=message, department='Marketing',
                                                      ticket_id=ticket_no):
                if await self.send_ticket_message_author(ctx=ctx, time_of_request=time_of_request,
                                                         department='Feature', ticket_id=ticket_no,
                                                         support_msg=message, colour=Colour.magenta()):
                    return
                else:
                    title = '__Support System Internal Error__'
                    message = f'System could deliver a copy of the ticket to your DM however ' \
                              f'support has recieved it and will be in touch as soon as possible. We apologize ' \
                              f'for inconvinience!'
                    await custom_message.system_message(ctx, message=message, color_code=1, destination=1,
                                                        sys_msg_title=title)
            else:
                title = '__Support System Internal Error__'
                message = f'System could not process you request at this moment. Please try again later. ' \
                          f'We apologize for inconvinience!'
                await custom_message.system_message(ctx, message=message, color_code=1, destination=1,
                                                    sys_msg_title=title)

        else:
            message = f'Message needs to be between 20 and 200 characters in length!'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)

    @sys.error
    async def sys_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = 'Message could not be send to developers because either it was not written on one of the public' \
                      ' channels, or you are now the owner of the guild.'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)


def setup(bot):
    bot.add_cog(StaffContactCmd(bot))
