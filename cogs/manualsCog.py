"""
COGS: used for help and support commands
"""

import os
import sys
from datetime import datetime
from uuid import uuid4

from discord import Embed, Colour, TextChannel
from discord.ext import commands

from cogs.toolsCog.checks import is_community_owner, is_overwatch
from cogs.toolsCog.systemMessages import CustomMessages
from utils.jsonReader import Helpers

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

custom_message = CustomMessages()
helper = Helpers()

bot_setup = helper.read_json_file(file_name='mainBotConfig.json')


class SupportAndHelpCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.support_channel_id = int(bot_setup["ticketSupportChannel"])

    @commands.command()
    @commands.check(is_community_owner)
    async def support(self, ctx, *, support_msg: str):
        support_channel = self.bot.get_channel(id=int(self.support_channel_id))
        if 20 <= len(support_msg) <= 200:
            if isinstance(ctx.message.channel, TextChannel):
                ticket_no = str(uuid4())
                time_of_request = datetime.utcnow()
                supp_msg = Embed(title='__Support requested__',
                                 colour=Colour.magenta(),
                                 timestamp=time_of_request)
                supp_msg.set_thumbnail(url=ctx.message.author.avatar_url)
                supp_msg.set_author(name=f'{ctx.message.author} id: {ctx.message.author.id}')
                supp_msg.add_field(name="From Guild",
                                   value=f'{ctx.message.guild} (ID: {ctx.message.guild.id}',
                                   inline=False)
                supp_msg.add_field(name="Ticket ID",
                                   value=ticket_no,
                                   inline=False)
                supp_msg.add_field(name="Message Content",
                                   value=f'{support_msg}',
                                   inline=False)
                await support_channel.send(content=f"TICKET: {ticket_no}")
                support_msg = await support_channel.send(embed=supp_msg)
                await support_msg.add_reaction(emoji="⛔")

                user_msg = Embed(title='__Support ticket issues successfully__',
                                 description='Automatic System Message',
                                 timestamp=time_of_request,
                                 colour=Colour.green())
                user_msg.set_thumbnail(url=self.bot.user.avatar_url)

                user_msg.add_field(name='Sys message',
                                   value=f'We would like to inform you that your support ticket has been'
                                         f' recieved successfully. One of the '
                                         f'support staff wiill be in contact with you in next 24 hours! '
                                         f'Thank your for {self.bot.user}',
                                   inline=False)
                user_msg.add_field(name="Reference Support Ticker Number",
                                   value=ticket_no,
                                   inline=False)
                user_msg.add_field(name="Reques message",
                                   value=f'{support_msg}',
                                   inline=False)
                user_msg.set_footer(text='Service provided by Launch Pad Investments')
                await ctx.author.send(embed=user_msg)

            else:
                message = "In order to issue support ticket you need to execute command  on public channel " \
                          "of the community where the bot is present."
                await custom_message.system_message(ctx=ctx, color_code=1, message=message, destination=0)
        else:
            message = 'Message is to short or to long!'
            await custom_message.system_message(ctx=ctx, color_code=1, message=message, destination=0)

    @commands.command()
    @commands.check(is_overwatch)
    async def support_reply(self, ctx, user_id: int, ticket_id: str, *, answer: str):
        time_of_response = datetime.utcnow()
        recipient = await self.bot.fetch_user(user_id=int(user_id))
        answer = Embed(title='__Support response message__',
                       colour=Colour.purple(),
                       timestamp=time_of_response)
        answer.set_thumbnail(url=self.bot.user.avatar_url)
        answer.add_field(name='Response to ticket ID:',
                         value=f'{ticket_id}',
                         inline=False)
        answer.add_field(name='Author',
                         value=f'{ctx.message.author}\n{ctx.message.author.id}',
                         inline=False)
        answer.add_field(name='Support Response',
                         value=f'{answer}',
                         inline=False)
        answer.set_footer(text='Service provided by Launch Pad Investments')
        await recipient.send(embed=answer)

    @support.error
    async def support_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = f'You can not create support tickert because you are not the owner of {ctx.message.guild}.'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        elif isinstance(error, commands.MissingRequiredArgument):
            message = f'You you have not provided all required arguments when creating support ticket.'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        elif isinstance(error, commands.BadArgument):
            message = f'You have provided bad arguments when creating support ticket. please try again'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)


def setup(bot):
    bot.add_cog(SupportAndHelpCommands(bot))
