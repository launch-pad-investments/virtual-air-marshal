import discord
from discord import ChannelType

from backoffice.jailSystemDb import JailSystemManager
from backoffice.spamSystemDb import SpamSystemManager
from backoffice.supportSystemDb import SupportSystemManager
from backoffice.loggerSystemDb import LoggerSystem

spam_sys_mng = SpamSystemManager()
jail_sys_mgn = JailSystemManager()
support_sys_mng = SupportSystemManager()
logger = LoggerSystem()


def is_spam_not_registered(ctx):
    return spam_sys_mng.check_if_not_registered(community_id=ctx.message.guild.id)


def is_spam_registered(ctx):
    return spam_sys_mng.check_community_reg_status(community_id=ctx.guild.id)


def is_public(ctx):
    return ctx.message.channel.type != ChannelType.private


def is_overwatch(ctx):
    access_list = [455916314238648340, 360367188432912385]
    return [member for member in access_list if member == ctx.message.author.id]


def is_community_owner(ctx):
    return ctx.message.author.id == ctx.message.guild.owner_id


def is_jail_not_registered(ctx):
    return jail_sys_mgn.check_if_jail_not_registered(community_id=ctx.message.guild.id)


def is_community_registered(ctx):
    return jail_sys_mgn.check_if_jail_registered(community_id=ctx.message.guild.id)


def is_jail_activated(message):
    return jail_sys_mgn.jail_activated(community_id=message.guild.id)


def is_support_not_registered(ctx):
    return support_sys_mng.check_if_not_registered(community_id=ctx.message.guild.id)


def is_support_registered(ctx):
    return support_sys_mng.check_community_reg_status(community_id=int(ctx.message.guild.id))


def check_if_support_channel_registered(ctx):
    return support_sys_mng.get_channel(community_id=int(ctx.message.guild.id)) > 0


def check_if_support_activated(ctx):
    return support_sys_mng.check_support_system_status(community_id=ctx.guild.id)


def is_text_channel(ctx):
    return isinstance(ctx.message.channel, discord.TextChannel)


def ban_predicate(ctx):
    return ctx.author.guild_permissions.ban_members


def kick_predicate(ctx):
    return ctx.author.guild_permissions.kick_members


def admin_predicate(ctx):
    return ctx.message.author.administrator


def role_mng(ctx):
    return ctx.author.manage_roles


def logger_registration_status(ctx):
    return logger.check_community_reg_status(community_id=ctx.guild.id)

