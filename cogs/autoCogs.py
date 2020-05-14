import os
import sys

import discord
from discord.ext import commands

from utils.jsonReader import Helpers
from .toolsCog.systemMessages import CustomMessages

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

helper = Helpers()
cust_messages = CustomMessages()

bot_setup = helper.read_json_file(file_name='mainBotConfig.json')


class AutoFunctions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        When member joins he will receive a greeting and will be forwarded to TOS channel. If
        automation of roles is turned on than he will need to read TOS and react with emoji,
        otherwise role Visitor will be assigned automatically
        :param member:
        :return:
        """
        if bot_setup['welcomeService'] == 1:
            if not member.bot:
                text = 'Hey, and welcome to the Launch Pad Investments. Please head to #the-landing-pad, read ' \
                       'the Terms of Service and if you agree, you will know what to do ;). Enjoy your stay!'

                sys_embed = discord.Embed(title="System Message",
                                          description="Welcome to Launch Pad Investments Community",
                                          colour=0x319f6b)
                sys_embed.add_field(name='Message',
                                    value=text)

                try:
                    await member.send(embed=sys_embed)
                except Exception:
                    print('pass')

            else:
                pass
        else:
            role = discord.utils.get(member.guild.roles, name=bot_setup['entryRole'])
            member.add_roles(role)

            sys_embed = discord.Embed(title="System Message",
                                      description="Access Granted",
                                      colour=0x319f6b)
            sys_embed.add_field(name='Message',
                                value="Welcome to Launch Pad Investment Community. Please head to #the-landing-pad and get familliar with out TOS")

            try:
                await member.send(embed=sys_embed)
            except Exception:
                print('pass')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        """
        Waits for reaction to specific message and once user agrees it will automatically sign role to him
        :param reaction: discord.Reaction
        :return: None
        """

        author = reaction.member  # Author of reaction

        # Check if user has responded with reaction to the mmessage with id on the specific channel
        if reaction.channel_id == bot_setup['reactionChannelId']:
            if reaction.message_id == bot_setup['reactionMessageId']:
                # Check if user reacted with thumbs up emoji
                if reaction.emoji.name == '\U0001F44D':
                    role = discord.utils.get(reaction.member.guild.roles, name=bot_setup['entryRole'])
                    await reaction.member.add_roles(role)

                    sys_embed = discord.Embed(title="System Message",
                                              description="Access granted",
                                              colour=0x319f6b)
                    sys_embed.add_field(name='Message',
                                        value="Welcome to Launch Pad Investment Community. Please head to #the-landing-pad and get familliar with out TOS")

                    try:
                        await author.send(embed=sys_embed)
                    except Exception:
                        print('pass')
                else:
                    message = 'You have either reacted with wrong emoji or than you did not want to accept Terms Of Service. Community has therefore stayed locked for you.'
                    title = f"Access to {reaction.guild} forbidden"
                    sys_embed = discord.Embed(title="System Message",
                                              description=title,
                                              colour=0x319f6b)
                    sys_embed.add_field(name='Message',
                                        value=message)
            else:
                print(f'In appropriate message ID {reaction.message_id}')
        else:
            print('This channel is not applied for services')


def setup(bot):
    bot.add_cog(AutoFunctions(bot))
