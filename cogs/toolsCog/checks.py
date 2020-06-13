import discord
from backoffice.spamSystemDb import SpamSystemManager
from backoffice.jailSystemDb import JailSystemManager

spam_sys_mng = SpamSystemManager()
jail_sys_mgn = JailSystemManager()

def is_spam_not_registered(ctx):
    return spam_sys_mng.check_if_not_registered(community_id=ctx.message.guild.id)

def is_public(ctx):
    return ctx.message.channel.type != discord.ChannelType.private

def is_overwatch(ctx):
    access_list = [455916314238648340, 360367188432912385]
    return [member for member in access_list if member == ctx.message.author.id]

def is_community_owner(ctx):
    return ctx.message.author.id == ctx.message.guild.owner_id

def is_jail_not_registered(ctx):
    return jail_sys_mgn.check_if_jail_not_registered(community_id=ctx.message.guild.id)

def is_community_registered(ctx):
    return jail_sys_mgn.check_if_jail_registered(community_id=ctx.message.guild.id)