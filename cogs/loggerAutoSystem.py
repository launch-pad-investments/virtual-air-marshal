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

    async def on_member_events(self, member, direction: int, channel_id: int, action: str, post=None):
        """
        Get triggered when member joins
        """
        ts = datetime.utcnow()
        c = self.get_direction_color(direction=direction)
        destination = self.bot.get_channel(id=channel_id)

        if not member.bot:
            member_info = Embed(title=f'***Member {action}***',
                                colour=c,
                                timestamp=ts)
            if action in ["Joined", "Left"]:
                member_info.add_field(name=f'Username',
                                      value=f'{member} ({member.id})',
                                      inline=False)
                member_info.add_field(name=f'Joined @',
                                      value=f'{member.joined_at}',
                                      inline=False)
                await destination.send(embed=member_info)
            elif action == "Update":
                if member.nicl != post.nick:
                    member_info.add_field(name=f'Nickname Changed',
                                          value=f'{member.nick} --> {post.nick}',
                                          inline=False)
                if member.status != post.status:
                    member_info.add_field(name=f'Status Updated:',
                                          value=f'{member.status} --> {post.status}',
                                          inline=False)
                if member.roles != post.roles:
                    # TODO create role names
                    member_info.add_field(name=f'Member Roles Update',
                                          value=f'{len(member.roles)} --> {len(post.roles)}',
                                          inline=False)

                if member.display_name != post.display_name:
                    member_info.add_field(name=f'Display Name changed',
                                          value=f'{member.display_name} --> {post.display_name}',
                                          inline=False)

                if member.top_role != post.top_role:
                    member_info.add_field(name=f'New Top Role assigned',
                                          value=f'{post.top_role}',
                                          inline=False)

            member_info.set_footer(text="Logged @ ", icon_url=self.bot.user.avatar_url)
            member_info.set_thumbnail(url=member.avatar_url)
            await destination.send(embed=member_info)
        else:
            if action in ["Joined", "Left"]:
                member_info = Embed(title=f'***Bot {action}***',
                                    colour=c,
                                    timestamp=ts)
                member_info.add_field(name=f'Bot Name',
                                      value=f'{member} ({member.id})',
                                      inline=False)
                member_info.add_field(name=f'Joined @',
                                      value=f'{member.joined_at}',
                                      inline=False)
                member_info.set_footer(text="Logged @ ", icon_url=self.bot.user.avatar_url)
                member_info.set_thumbnail(url=member.avatar_url)
                await destination.send(embed=member_info)

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
            chn_created = channel.created_at
            chn_id = channel.id
            chn = f'{channel}'
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
            pre_category = pre.category
            pre_chn_id = pre.id
            pre_chn_name = f'{pre}'
            pre_chn_topic = pre.topic
            pre_chn_type = pre.type

            post_category = post.category
            post_chn_name = f'{post}'
            post_chn_topic = f'{post.topic}'
            post_chn_type = post.type

            msg_related = Embed(title=f'***Voice Channel*** {action}',
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

        elif isinstance(pre, discord.CategoryChannel):
            category_id = pre.id
            category_pre = f'{pre}'
            category_post = f'{post}'
            category_pre_pos = pre.position
            category_post_pos = post.position
            category_pre_nsf = pre.is_nsfw()
            category_post_nsfw = post.is_nsfw()

            category_related = Embed(title=f'***Category Channel*** {action}',
                                     colour=c,
                                     timestamp=ts)
            category_related.add_field(name='Category modified"',
                                       value=f'{category_pre} (id:{category_id})',
                                       inline=False)
            if category_pre != category_post:
                category_related.add_field(name='Category Name Changed:',
                                           value=f'{category_pre} -> {category_post}',
                                           inline=False)

            if category_pre_pos != category_post_pos:
                category_related.add_field(name='Category Position Change from ',
                                           value=f'#{category_pre_pos} -> {category_post_pos}',
                                           inline=False)

            if category_pre_nsf != category_post_nsfw:
                category_related.add_field(name='Category Nsfw Changed ',
                                           value=f'{category_post_nsfw}',
                                           inline=False)

            category_related.set_footer(text="Logged @ ", icon_url=self.bot.user.avatar_url)
            await destination.send(embed=category_related)

    async def role_actions(self, channel_id, role, direction: int, action: str, post=None):
        ts = datetime.utcnow()
        c = self.get_direction_color(direction=direction)
        destination = self.bot.get_channel(id=channel_id)
        role_id = role.id
        role_name = f"{role}"
        hoist = role.hoist  # Is separated or not from toher
        role_position = role.position
        role_mentionable = role.mentionable  # True or false
        role_permissions = role.permissions  # Iteerable?
        role_created = role.created_at
        role_mention = role.mention

        role_stuff = Embed(title=f'***Role {action}***',
                           colour=c,
                           timestamp=ts)

        if action == 'Update':
            post_role = f"{post}"
            hoist_pos = post.hoist  # Is separated or not from toher
            post_position = post.position
            role_mentionable_post = post.mentionable  # True or false
            role_permissions_post = post.permissions  # Iteerable?
            role_mention_post = post.mention

            if post_role != role_name:
                role_stuff.add_field(name=f'Role name Changed',
                                     value=f'{role_name} --> {post_role})',
                                     inline=False)

            if hoist_pos != hoist:
                role_stuff.add_field(name=f'Hoist status:',
                                     value=f'{hoist} --> {hoist_pos}',
                                     inline=False)

            if role_position != post_role:
                role_stuff.add_field(name=f'Role Position Changed:',
                                     value=f'{role_position} --> {post_position}',
                                     inline=False)

            if role_mentionable != role_mentionable_post:
                role_stuff.add_field(name=f'Role Mention Permission:',
                                     value=f'{role_mentionable} --> {role_mentionable_post}',
                                     inline=False)

            if role_permissions != role_permissions_post:
                role_stuff.add_field(name=f'Role permissons updated:',
                                     value=f'{role_permissions_post}',
                                     inline=False)

            await destination.send(embed=role_stuff)

        elif action == 'Created':
            role_stuff.add_field(name=f'Role Name',
                                 value=f'{role_name} {role_mention} ({role_id})',
                                 inline=False)
            role_stuff.add_field(name=f'Created at',
                                 value=f'{role_created})')
            role_stuff.add_field(name=f'Role rank',
                                 value=f'#{role_position}')
            role_stuff.add_field(name=f'Hoist status:',
                                 value=f'{hoist}')
            role_stuff.add_field(name=f'Mentionable',
                                 value=f'{role_mentionable}')
            role_stuff.add_field(name=f'Permissions',
                                 value=f'{role_permissions}')
            await destination.send(embed=role_stuff)

        elif action == 'Deleted':
            role_stuff.add_field(name=f'Role Name',
                                 value=f'{role_name} {role_mention} ({role_id})',
                                 inline=False)
            role_stuff.add_field(name=f'Created at',
                                 value=f'{role_created})')
            role_stuff.add_field(name=f'Role rank',
                                 value=f'#{role_position}')
            role_stuff.add_field(name=f'Hoist status:',
                                 value=f'{hoist}')
            role_stuff.add_field(name=f'Mentionable',
                                 value=f'{role_mentionable}')
            role_stuff.add_field(name=f'Permissions',
                                 value=f'{role_permissions}')

        await destination.send(embed=role_stuff)

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

    async def message_pin_action(self, channel_id, channel, last_pin, direction=2):
        ts = datetime.utcnow()
        c = self.get_direction_color(direction=direction)
        destination = self.bot.get_channel(id=channel_id)

        chn_category = channel.category
        chn_pins = channel.pins
        print(chn_pins)

        #
        # pprint(dir(last_pin))
        # print(last_pin)

    @commands.Cog.listener()
    async def on_guild_channel_pins_update(self, channel, last_pin):
        if self.check_logger_status(guild_id=channel.guild.id):
            channel_id = logger.get_channel(community_id=channel.guild.id)
            await self.message_pin_action(channel_id=channel_id, channel=channel, last_pin=last_pin, direction=2)
        else:
            pass

    @commands.Cog.listener()
    async def on_webhooks_update(self, channel):
        pass

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if self.check_logger_status(guild_id=member.guild.id):
            channel_id = logger.get_channel(community_id=member.guild.id)
            await self.on_member_events(member=member, direction=1, channel_id=int(channel_id), action='Left')
        else:
            pass

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if self.check_logger_status(guild_id=member.guild.id):
            channel_id = logger.get_channel(community_id=member.guild.id)
            await self.on_member_events(member=member, direction=1, channel_id=int(channel_id), action='Joined')
        else:
            pass

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        if self.check_logger_status(guild_id=guild.id):
            channel_id = logger.get_channel(community_id=guild.id)
            await self.on_member_events(member=user, direction=1, channel_id=int(channel_id), action='Banned')
        else:
            pass

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        if self.check_logger_status(guild_id=guild.id):
            channel_id = logger.get_channel(community_id=guild.id)
            await self.on_member_events(member=user, direction=1, channel_id=int(channel_id), action='Unbanned')
        else:
            pass

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if self.check_logger_status(guild_id=before.guild.id):
            channel_id = logger.get_channel(community_id=before.guild.id)
            await self.on_member_events(member=before, direction=2, channel_id=channel_id, action="Update", post=after)
        else:
            pass

    @commands.Cog.listener()
    async def on_user_update(self, before, ufter):
        pass

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        if self.check_logger_status(guild_id=role.guild.id):
            channel_id = logger.get_channel(community_id=role.guild.id)
            await self.role_actions(channel_id=channel_id, role=role, direction=1, action='Created')
        else:
            pass

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        if self.check_logger_status(guild_id=role.guild.id):
            channel_id = logger.get_channel(community_id=role.guild.id)
            await self.role_actions(channel_id=channel_id, role=role, direction=0, action='Deleted')
        else:
            pass

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        if self.check_logger_status(guild_id=before.guild.id):
            channel_id = logger.get_channel(community_id=before.guild.id)
            await self.role_actions(channel_id=channel_id, role=before, direction=0, action='Deleted', post=after)
        else:
            pass

    # discord.on_guild_emojis_update(guild, before, after)
    # discord.on_voice_state_update(member, before, after)

    # discord.on_invite_create(invite)
    # discord.on_invite_delete(invite)¶
    # discord.on_group_join(channel, user)
    # discord.on_group_remove(channel, user)
    # discord.on_relationship_add(relationship)
    # discord.on_relationship_remove(relationship)
    # discord.on_relationship_update(before, after)


def setup(bot):
    bot.add_cog(LoggerAutoSystem(bot))
