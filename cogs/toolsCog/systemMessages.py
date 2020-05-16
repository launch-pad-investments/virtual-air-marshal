import os
import sys

import discord
from discord import Member as DiscordMember

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)


class CustomMessages:
    def __init__(self):
        pass

    async def user_message(self, message, description, color_code: int, to_user: DiscordMember):

        if color_code == 0:
            signal = 0x319f6b
        else:
            signal = discord.Colour.red()

        sys_embed = discord.Embed(title="System Message",
                                  description=description,
                                  colour=signal)
        sys_embed.add_field(name='Message',
                            value=message)

        try:
            await to_user.send(embed=sys_embed)
        except Exception as e:
            print(e)

    async def embed_builder(self, ctx, title, description, data: list, destination=None):
        """
        Build embed from data provided
        :param ctx: Discord Context
        :param title: Title for embed
        :param description: Description of embed
        :param data: data as list of dict
        :return:
        """
        emb = discord.Embed(title=title,
                            description=description,
                            colour=discord.Colour.gold())
        for d in data:
            emb.add_field(name=d['name'],
                          value=d['value'],
                          inline=False)

        if destination:
            await ctx.author.send(embed=emb)
        else:
            await ctx.channel.send(embed=emb, delete_after=40)

    async def system_message(self, ctx, color_code: int, message: str, destination: int, sys_msg_title: str = None):
        if color_code == 0:
            signal = 0x319f6b
        else:
            signal = discord.Colour.red()

        if sys_msg_title is None:
            sys_msg_title = 'System Message'
        else:
            pass

        sys_embed = discord.Embed(title="System Message",
                                  description=sys_msg_title,
                                  colour=signal)
        sys_embed.add_field(name='Message',
                            value=message)

        if destination == 0:
            await ctx.author.send(embed=sys_embed)
        else:
            await ctx.channel.send(embed=sys_embed, delete_after=100)