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

    async def send_message_edit(self, pre: discord.Message, post: discord.Message, direction: int, action: str,
                                channel_id):
        pre_content = pre.content
        post_content = post.content
        ts = datetime.utcnow()

        c = self.get_direction_color(direction=direction)
        destination = self.bot.get_channel(id=channel_id)

        msg_related = Embed(title=f'***Message*** {action} ',
                            colour=c,
                            timestamp=ts)
        msg_related.add_field(name='Channel',
                              value=f'{pre.channel} (id:{pre.channel.id})',
                              inline=False)
        msg_related.add_field(name='Jump Url',
                              value=post.jump_url,
                              inline=False)
        msg_related.add_field(name='Original',
                              value=f'{pre_content}',
                              inline=False)
        msg_related.add_field(name='Edited',
                              value=f'{post_content}',
                              inline=False)
        msg_related.add_field(name=f'Created at',
                              value=f'{pre.created_at}')
        msg_related.set_author(name=f'{post.author} id:{post.author.id}', icon_url=f'{post.author.avatar_url}')
        msg_related.set_footer(text="Logged @ ", icon_url=self.bot.user.avatar_url)
        await destination.send(embed=msg_related)

    async def send_message_deleted(self, channel_id, message: discord.Message, direction: int, action: str):
        ts = datetime.utcnow()
        c = self.get_direction_color(direction=direction)
        destination = self.bot.get_channel(id=channel_id)
        created_at = message.created_at
        author = message.author
        content = message.content[:100]
        message_type = message.type
        channel_of_message = message.channel
        channel_id = message.channel.id
        is_pinned = message.pinned

        msg_related = Embed(title=f'***Message*** {action}',
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

    async def channel_actions(self, channel_id, channel, direction: int, action: str):
        ts = datetime.utcnow()
        c = self.get_direction_color(direction=direction)
        destination = self.bot.get_channel(id=channel_id)
        if isinstance(channel, discord.TextChannel):
            chn_category = channel.category
            chn_created = channel.created_at
            chn_id = channel.id
            chn = f'{channel}'
            chn_topic = channel.topic
            chn_type = channel.type

            msg_related = Embed(title=f'***Channel*** {action}',
                                colour=c,
                                timestamp=ts)
            msg_related.add_field(name='Channel',
                                  value=f'{chn} (id:{chn_id})',
                                  inline=False)
            msg_related.add_field(name=f'Created at',
                                  value=f'{chn_created}',
                                  inline=False)
            msg_related.add_field(name=f'Channel Type',
                                  value=f'{chn_type}',
                                  inline=False)
            msg_related.add_field(name=f'Channel Category',
                                  value=f'{chn_category}',
                                  inline=False)
            msg_related.add_field(name=f'Channel Topic',
                                  value=f'{chn_topic}',
                                  inline=False)
            msg_related.set_footer(text="Logged @ ", icon_url=self.bot.user.avatar_url)
            await destination.send(embed=msg_related)

        elif isinstance(channel, discord.VoiceChannel):
            chn_category = channel.category
            chn_created = channel.created_at
            chn_id = channel.id
            chn = f'{channel}'
            chn_type = channel.type
            msg_related = Embed(title=f'***Voice Channel*** {action}',
                                colour=c,
                                timestamp=ts)
            msg_related.add_field(name='Voice Channel',
                                  value=f'{chn} (id:{chn_id})',
                                  inline=False)
            msg_related.add_field(name=f'Created at',
                                  value=f'{chn_created}',
                                  inline=False)
            msg_related.add_field(name=f'Channel Type',
                                  value=f'{chn_type}',
                                  inline=False)
            msg_related.add_field(name=f'Channel Category',
                                  value=f'{chn_category}',
                                  inline=False)
            msg_related.set_footer(text="Logged @ ", icon_url=self.bot.user.avatar_url)
            await destination.send(embed=msg_related)

        elif isinstance(channel, discord.CategoryChannel):
            chn_category = channel.category
            chn_created = channel.created_at
            chn_id = channel.id
            chn = f'{channel}'
            chn_type = channel.type
            msg_related = Embed(title=f'***Channel Category *** {action}',
                                colour=c,
                                timestamp=ts)
            msg_related.add_field(name='Category Name',
                                  value=f'{chn} (id:{chn_id})',
                                  inline=False)
            msg_related.add_field(name=f'Created at',
                                  value=f'{chn_created}',
                                  inline=False)
            msg_related.set_footer(text="Logged @ ", icon_url=self.bot.user.avatar_url)
            await destination.send(embed=msg_related)

    async def channel_edited(self, channel_id, pre, post, direction: int, action: str):
        ts = datetime.utcnow()
        c = self.get_direction_color(direction=direction)
        destination = self.bot.get_channel(id=channel_id)

        if isinstance(pre, discord.TextChannel):
            pre_category = pre.category
            pre_chn_id = pre.id
            pre_chn_name = f'{pre}'
            pre_chn_topic = pre.topic
            pre_chn_type = pre.type

            post_category = post.category
            post_chn_name = f'{post}'
            post_chn_topic = f'{post.topic}'
            post_chn_type = post.type

            msg_related = Embed(title=f'***Text Channel*** {action}',
                                colour=c,
                                timestamp=ts)
            msg_related.add_field(name='Channel modified"',
                                  value=f'{pre} (id:{pre_chn_id})',
                                  inline=False)
            
            if pre_chn_name != post_chn_name:
                msg_related.add_field(name='Channel Name Changed:',
                                      value=f'{pre_chn_name} -> {post_chn_name}',
                                      inline=False)

            if pre_chn_topic != post_chn_topic:
                msg_related.add_field(name='Channel Topic Changed:',
                                      value=f'{pre_chn_topic} -> {post_chn_topic}',
                                      inline=False)

            if pre_chn_type != post_chn_type:
                msg_related.add_field(name='Channel Type Changed:',
                                      value=f'{pre_chn_type} -> {post_chn_type}',
                                      inline=False)

            if pre_category != post_category:
                msg_related.add_field(name='Channel Category Changed:',
                                      value=f'{pre_category} -> {post_category}',
                                      inline=False)

            msg_related.add_field(name=f'Channel Type',
                                  value=f'{pre_chn_type}',
                                  inline=False)

            msg_related.set_footer(text="Logged @ ", icon_url=self.bot.user.avatar_url)
            await destination.send(embed=msg_related)

        elif isinstance(pre, discord.VoiceChannel):
            pass

        elif isinstance(pre, discord.CategoryChannel):
            pass

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """
        Triggered when message deleted
        """
        if not message.author.bot:
            if self.check_logger_status(message.guild.id):
                channel_id = logger.get_channel(community_id=message.guild.id)
                await self.send_message_deleted(channel_id=channel_id, message=message, direction=0, action='Deleted')
            else:
                pass
        else:
            pass

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """
        Triggered when message edited
        """
        if not before.author.bot:
            if self.check_logger_status(before.guild.id):
                channel_id = logger.get_channel(community_id=before.guild.id)
                await self.send_message_edit(pre=before, post=after, direction=2, action="Edited",
                                             channel_id=channel_id)
            else:
                pass
        else:
            pass

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        """
        Triggered when channel deleted
        """
        if self.check_logger_status(guild_id=channel.guild.id):
            channel_id = logger.get_channel(community_id=channel.guild.id)
            await self.channel_actions(channel_id=channel_id, channel=channel, direction=0, action='Deleted')
        else:
            pass

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        """
        Triggered when channel created
        """
        if self.check_logger_status(guild_id=channel.guild.id):
            channel_id = logger.get_channel(community_id=channel.guild.id)
            await self.channel_actions(channel_id=channel_id, channel=channel, direction=1, action='Created')
        else:
            pass

    @commands.Cog.listener()
    async def on_guild_channel_update(self, pre, post):
        if self.check_logger_status(guild_id=pre.guild.id):
            channel_id = logger.get_channel(community_id=pre.guild.id)
            await self.channel_edited(channel_id=channel_id, pre=pre, post=post, direction=2, action='Updated')
        else:
            pass


def setup(bot):
    bot.add_cog(LoggerAutoSystem(bot))
