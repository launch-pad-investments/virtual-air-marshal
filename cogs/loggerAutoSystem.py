import os
import sys
import time
from datetime import datetime, timedelta
from pprint import pprint
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
            # If someone leaves or delition happens
            return Colour.red()
        elif direction == 1:
            # If someone joins and good happens
            return Colour.green()
        elif direction == 2:
            return Colour.orange()
        
    async def send_member_related_messages(self, channel_id, member: discord.Member, direction: int):

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

    async def send_message_related(self, channel_id, message: discord.Message, direction: int, action:str, post:discord.Message = None):
        #TODO integrate message check if its edited

        ts = datetime.utcnow()
        c = self.get_direction_color(direction=direction)
        destination = self.bot.get_channel(id=channel_id)
        created_at = message.created_at
        author = message.author
        author_id = message.author.id
        content = message.content [:100]
        message_type = message.type
        channel_of_message = message.channel
        channel_id = message.channel.id
        is_pinned = message.pinned

        msg_related = Embed(title=f'***Message*** {action} ',
                            colour=c,
                            timestamp=ts)
        msg_related.add_field(name='Channel',
                              value=f'{channel_of_message} (id:{channel_id})',
                              inline=False)
        msg_related.add_field(name=f'Message Type',
                              value=f'{message_type}',
                              inline=False)
        msg_related.add_field(name=f'Pin Status',
                              value=f'{is_pinned}')
        msg_related.add_field(name='Message content',
                              value=f'{content}',
                              inline=False)
        msg_related.add_field(name=f'Created at',
                              value=f'{created_at}')
        msg_related.set_author(name=f'{author} id:{author.id}', icon_url=f'{author.avatar_url}')
        msg_related.set_footer(text="Logged @ ", icon_url=self.bot.user.avatar_url)
        await destination.send(embed=msg_related)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.author.bot:
            if self.check_logger_status(message.guild.id):
                channel_id = logger.get_channel(community_id=message.guild.id)
                await self.send_message_related(channel_id=channel_id, message=message, direction=0,action='Deleted')
            else:
                pass
        else:
            print('Message was from bot')

    @commands.Cog.listener()
    async def on_message_edit(self, pre,post):
        pass


    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        Log when member joins community
        """
        if self.check_logger_status(guild_id=member.guild.id):
            channel_id = logger.get_channel(community_id=member.guild.id)
            await self.send_member_related_messages(channel_id=channel_id, member=member,direction=1)
        else:
            pass

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """
        Log when member leaves the community
        """
        if self.check_logger_status(guild_id=member.guild.id):
            channel_id = logger.get_channel(community_id=member.guild.id)
            await self.send_member_related_messages(channel_id=channel_id, member=member, direction=0)
        else:
            pass






def setup(bot):
    bot.add_cog(LoggerAutoSystem(bot))
