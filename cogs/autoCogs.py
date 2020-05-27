import os
import sys
from colorama import Fore

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)


import discord
from discord.ext import commands
from datetime import datetime, timedelta
import time

from utils.jsonReader import Helpers
from toolsCog.systemMessages import CustomMessages
from jailList import JailManagement

jail_manager = JailManagement()
helper = Helpers()
cust_messages = CustomMessages()

bot_setup = helper.read_json_file(file_name='mainBotConfig.json')
CONT_JAIL_DURATION = 2


class AutoFunctions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bad_words = helper.read_json_file('badWords.json')['words']   

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
                
                #TODO give him a unverified role
                print(Fore.BLUE + f"New user joined community: {member} (ID: {member.id})")
                role = discord.utils.get(member.guild.roles, name="UNVERIFIED")
                await member.add_roles(role)
                print(Fore.YELLOW + "Role Unveriffied give to the user {member} with ID: {member.id}")
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
                    pass

            else:
                pass
        else:
            print(Fore.BLUE + f"New user joined community: {member} (ID: {member.id})")
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
                        pass
                    
                    print(Fore.GREEN + f"User accepted TOS {author} (ID: {author.id}")
                else:
                    message = 'You have either reacted with wrong emoji or than you did not want to accept Terms Of Service. Community has therefore stayed locked for you.'
                    title = f"Access to {reaction.guild} forbidden"
                    sys_embed = discord.Embed(title="System Message",
                                              description=title,
                                              colour=0x319f6b)
                    sys_embed.add_field(name='Message',
                                        value=message)
            else:
                pass
        else:
            pass
            
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot: 
            if message.guild.id == 667607865199951872:
                role = message.guild.get_role(role_id=667623277430046720)  # Get the role
                if role not in message.author.roles:
                    bad_count = [word for word in message.content.lower().split() if word in self.bad_words]
                    if bad_count:
                        if not jail_manager.check_if_jailed(discord_id=int(message.author.id)):            
                            user_id = message.author.id
                            if jail_manager.check_if_in_counter(discord_id=user_id):
                                current_score = jail_manager.increase_count(discord_id=user_id)
                                if current_score >= 3:
                                    # Current time
                                    start = datetime.utcnow()

                                    # Set the jail expiration to after one hour
                                    td = timedelta(minutes=int(CONT_JAIL_DURATION))
                                    # calculate future date
                                    end = start + td
                                    expiry = (int(time.mktime(end.timetuple())))
                                    
                                    end_date_time_stamp = datetime.utcfromtimestamp(expiry)
                                                                        
                                    guild = self.bot.get_guild(id=667607865199951872)  # Get guild
                                    active_roles = [role.id for role in message.author.roles][1:] # Get active roles
                                    
                                    # Throw to jail                        
                                    if jail_manager.throw_to_jail(discord_id=int(user_id),end=expiry, roleIds=active_roles):
                                        # Remove from counter
                                        if jail_manager.remove_from_counter(discord_id=int(user_id)):
                                            
                                            # Send message
                                            jailed_info = discord.Embed(title='__You have been jailed!__',
                                                                        description=' You have been automatically jailed, since you have broken the'
                                                                        'communication rules on community 3 times in a row. Next time be more cautious'
                                                                        ' on how you communicate',
                                                                        color = discord.Color.red())
                                            jailed_info.add_field(name=f'Jail time duration:',
                                                                value=f'{CONT_JAIL_DURATION} minutes')
                                            jailed_info.add_field(name=f'Sentence started @:',
                                                                value=f'{start} UTC')
                                            jailed_info.add_field(name=f'Sentece end on:',
                                                                value=f'{end_date_time_stamp} UTC')
                                            
                                            await message.author.send(embed=jailed_info)
                                            await message.channel.send(content=':cop:', delete_after = 60)
                                            
                                            # Jailing time
                                            guild = self.bot.get_guild(id=667607865199951872)
                                            # member = guild.get_member(message.author.id)                
                                            role = guild.get_role(710429549040500837)
                                            await message.author.add_roles(role, reason='Jailed......')       
                                            print(Fore.RED + f'User {message.author} has been jailed!!!!')
                                                                                       
                                            for role in active_roles:
                                                role = guild.get_role(role_id=int(role))  # Get the role
                                                await message.author.remove_roles(role, reason='Jail time served')
                                            
                                else: 
                                    await message.channel.send(content=f'{message.author.mention} You have received your {current_score}. strike. When you reach 3...you will be spanked!', delete_after = 10)
                            else:
                                jail_manager.apply_user(discord_id=user_id)
                                await message.channel.send(content='You have received your first strike. once you reach 3...you will be spanked and thrown to jail where only Animus can save you', delete_after=50)
                                await message.delete()
                        else:                       
                            await message.author.send(content='You have been put in the LaunchPad Prison. Send a DM to an admin to grant you bail, or sit your time out.')
                            await message.delete()
                    else:
                        pass
                else:
                    pass
            else:
                pass
        else:
            pass

def setup(bot):
    bot.add_cog(AutoFunctions(bot))