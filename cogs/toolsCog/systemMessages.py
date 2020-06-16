import os
import sys

from discord import Member as DiscordMember
from discord import Embed, Colour


project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)


class CustomMessages:
    def __init__(self):
        pass

    async def user_message(self, message, description, color_code: int, to_user: DiscordMember):

        if color_code == 0:
            signal = 0x319f6b
        else:
            signal = Colour.red()

        sys_embed = Embed(title="System Message",
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
        emb = Embed(title=title,
                            description=description,
                            colour=Colour.gold())
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
            signal = Colour.red()

        if sys_msg_title is None:
            sys_msg_title = '__System Message__'
        else:
            pass

        sys_embed = Embed(title="__System Message__",
                                  description=sys_msg_title,
                                  colour=signal)
        sys_embed.add_field(name='Message',
                            value=message)
        sys_embed.set_footer(text='This product is property of Launc Pad Investments group')

        if destination == 0:
            await ctx.author.send(embed=sys_embed)
        else:
            await ctx.channel.send(embed=sys_embed, delete_after=100)
            
    async def bug_messages(self, ctx, error, destination):
        animus_embed = Embed(title='Bug notifcationa', 
                             description=':bug: was found, below are details',
                             Colour=Colour.magenta())

        animus_embed.add_field(name='Error details',
                               value=f'{error}',
                               inline=False)
        animus_embed.add_field(name='Community',
                               value=f'{ctx.message.guild} id: {ctx.message.guild.id}',
                               inline=False)
        animus_embed.add_field(name='Author of command',
                               value=f'{ctx.message.author} id: {ctx.message.author.id}',
                               inline=False)
        animus_embed.add_field(name='Command written',
                               value=f'{ctx.message.content}',
                               inline=False)
        await destination.send(embed=animus_embed)