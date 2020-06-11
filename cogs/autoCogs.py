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
from backoffice.communityProfilesDb import SpamSystemManager

jail_manager = JailManagement()
helper = Helpers()
cust_messages = CustomMessages()
spam_sys_mng  = SpamSystemManager()

bot_setup = helper.read_json_file(file_name='mainBotConfig.json')
CONT_JAIL_DURATION = 2


class AutoFunctions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bad_words = helper.read_json_file('badWords.json')['words']
        # self.active_jails = community_manager.get_active_jails()
        
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        On member join role handling and spam protection
        :param member:
        :return:
        """
        print('New member joining')
        if not member.bot:
            sec_value = spam_sys_mng.check_if_security_activated(community_id=int(member.guild.id))
            if sec_value == 1:
                details = spam_sys_mng.get_details_of_channel(community_id = member.guild.id) # Get details of channel as dict
                role = discord.utils.get(member.guild.roles, name="Unverified")  # Check if role can be found if not than None
                if role:
                    await member.add_roles(role)  # Give member a role
                    #Console printoutn
                    print(Fore.BLUE + f"New user joined community: {member} (ID: {member.id})")
                    print(Fore.YELLOW + f"Role Unveriffied given to the user {member} with ID: {member.id}")
                    text = f'Hey and welcome to the {member.guild}. '
                    f'Head to channel #{details["appliedChannelName"]} '
                    f'(ID: {details["appliedChannelId"]}) and accept TOS/Rules of community!'

                    sys_embed = discord.Embed(title="__Air Marshal System Message__",
                                            description="This is auto-message!",
                                            colour=0x319f6b)
                    sys_embed.add_field(name='Message',
                                        value=text,
                                        inline=False)
                    sys_embed.set_thumbnail(url=self.bot.user.avatar_url)
                    sys_embed.set_footer(text='Service provided by Launch Pad Investments')

                    try:
                        await member.send(embed=sys_embed)
                        print(Fore.YELLOW + f"Message with instructions sent to {member} with ID: {member.id}")
                    except Exception:
                        print(Fore.RED + f"Message with instructions could not be delivered to {member} with ID: {member.id} due to no DM rule")
                        pass
                else:
                    print(Fore.RED + f"Role Unverified does not eexist on guild {member.guild} with id {member.guild.id}")  
                
            # Give user verified role
            elif sec_value == 0:
                # Auto role if system is off
                print(Fore.BLUE + f"New user joined community: {member} (ID: {member.id})")
                role = discord.utils.get(member.guild.roles, name='Visitor')
                
                if role:
                    await member.add_roles(role)
                    
                    print(Fore.YELLOW + f"Role Visitor given to the user {member} with ID: {member.id}")
                    text = f'Hey and welcome to the {member.guild}. '
                    f'Head to channel #{details["appliedChannelName"]} '
                    f'(ID: {details["appliedChannelId"]}) and familiarize yourself with TOS/Rules of community and enjoy jour stay!'
                    
                    sys_embed = discord.Embed(title=":rocket: __Air Marshal System Message__ :rocket:",
                                            description=f"Access to {member.guild} granted!",
                                            colour=0x319f6b)
                    sys_embed.add_field(name='__Notice!__',
                                        value=text)

                    try:
                        await member.send(embed=sys_embed)
                    except Exception:
                        print('pass')
                        
                        
                    text = f'{member.guild} uses {self.bot.user} which is a product of Launch Pad Investment Discord Group. '
                    f' It has been designed with the reason to allow moderation of the community.'
                    
                    sys_embed = discord.Embed(title=":rocket: __Air Marshal System Message__ :rocket:",
                                            description=f"Air-Marshal monitoring you activity :robot: ",
                                            colour=0x319f6b)
                    sys_embed.add_field(name='__Notice!__',
                                        value=text)

                    try:
                        await member.send(embed=sys_embed)
                    except Exception:
                        print(Fore.RED + f"Message with instructions could not be delivered to {member} with ID: {member.id} due to no DM rule")
                        pass
                else:
                    print(Fore.RED + f"Role Visitor does not exist on guild {member.guild} with id {member.guild.id}")  
                    
            # Nothing to do as it is not registered
            elif sec_value == 2:
                print(Fore.LIGHTWHITE_EX + f'Community {member.guild} not registered for the service')
                
        else:
            print(Fore.LIGHTWHITE_EX + f'{member} is BOT who joined {member.guild} with ID {member.guild.id}')
            
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        """
        Waits for reaction to specific message and once user agrees it will automatically sign role to him
        :param reaction: discord.Reaction
        :return: None
        """

        author = reaction.member  # Author of reaction
        details = spam_sys_mng.get_details_of_channel(community_id = author.guild.id)
        # Check if user has responded with reaction to the message with id on the specific channel
        if reaction.channel_id == details['appliedChannelId']:
            if reaction.message_id == details['appliedMessageId']:
                # Check if user reacted with thumbs up emoji
                if reaction.emoji.name == '\U0001F44D':
                    role = discord.utils.get(reaction.member.guild.roles, name='Visitor')
                    
                    if role:
                        await reaction.member.add_roles(role)
                        print(Fore.YELLOW + f"Role Visitor given to the user {author} with ID: {author.id}")
                        
                        text = f'Hey and welcome to the {author.guild}. '
                        f'You have successfully verified yourself, and gave yourself a chance to look through its content. Enjoy Your Stay!'
                        
                        sys_embed = discord.Embed(title=":rocket: __Air Marshal System Message__ :rocket:",
                                                description=f"Access to {author.guild} granted!",
                                                colour=0x319f6b)
                        sys_embed.add_field(name='__Notice!__',
                                            value=text)

                        try:
                            await author.send(embed=sys_embed)
                        except Exception:
                            print(Fore.RED + f"Welcome message could not be delivered to {author} with ID: {author.id} due to no DM rule")
                            pass
                            
                            
                        text = f'{author.guild} uses {self.bot.user} which is a product of Launch Pad Investment Discord Group. '
                        f' It has been designed with the reason to allow moderation of the community.'
                        
                        sys_embed = discord.Embed(title=":rocket: __Air Marshal System Message__ :rocket:",
                                                description=f"Air-Marshal monitoring you activity :robot: ",
                                                colour=0x319f6b)
                        sys_embed.add_field(name='__Notice!__',
                                            value=text)

                        try:
                            await author.send(embed=sys_embed)
                        except Exception:
                            print(Fore.RED + f"Welcome message could not be delivered to {author} with ID: {author.id} due to no DM rule")
                            pass
                    
                        print(Fore.CYAN + f"Removing the Unverified role from {author} (ID: {author.id}")
                        role_rmw = discord.utils.get(author.guild.roles, name="Unverified")
                        await author.remove_roles(role_rmw, reason='User accepted TOS')
                        print(Fore.YELLOW + f"Role Unverified removed from user {author} with ID: {author.id}")
                        print(Fore.GREEN + f"User accepted TOS {author} (ID: {author.id}")
                    else:
                        print(Fore.RED + f"Role Visitor does not exist on guild {author.guild} with id {author.guild.id}")  
                else:
                    message = 'You have either reacted with wrong emoji or than you did not want to accept Terms Of Service. Community has therefore stayed locked for you.'
                    title = f"Access to {reaction.guild} forbidden"
                    sys_embed = discord.Embed(title="System Message",
                                              description=title,
                                              colour=0x319f6b)
                    sys_embed.add_field(name='Message',
                                        value=message)
            else:
                message = f'You have reacted to wrong message! Message ID is {details["appliedMessageId"]}!'
                title = f":octagonal_sign:  __Air Marshal System Message__ :octagonal_sign: "
                sys_embed = discord.Embed(title="System Message",
                                            description=title,
                                            colour=0x319f6b)
                sys_embed.add_field(name='Message',
                                    value=message)
        else:
            pass
            
    
    # @commands.Cog.listener()
    # async def on_message(self, message):
    #     """
    #     Bad word checker!
    #     """

    #     if not message.author.bot: 
    #         if message.guild.id in self.active_jails:  # If guild has active jail
    #             role = message.guild.get_role(role_id=667623277430046720)  # Get the role
    #             if role not in message.author.roles:
    #                 bad_count = [word for word in message.content.lower().split() if word in self.bad_words]
    #                 if bad_count:
    #                     if not jail_manager.check_if_jailed(discord_id=int(message.author.id)):            
    #                         user_id = message.author.id
    #                         if jail_manager.check_if_in_counter(discord_id=user_id):
    #                             current_score = jail_manager.increase_count(discord_id=user_id)
    #                             if current_score >= 3:
    #                                 # Current time
    #                                 start = datetime.utcnow()

    #                                 # Set the jail expiration to after one hour
    #                                 td = timedelta(minutes=int(CONT_JAIL_DURATION))
    #                                 # calculate future date
    #                                 end = start + td
    #                                 expiry = (int(time.mktime(end.timetuple())))
                                    
    #                                 end_date_time_stamp = datetime.utcfromtimestamp(expiry)
                                                                        
    #                                 guild = self.bot.get_guild(id=667607865199951872)  # Get guild
    #                                 active_roles = [role.id for role in message.author.roles][1:] # Get active roles
                                    
    #                                 # Throw to jail                        
    #                                 if jail_manager.throw_to_jail(discord_id=int(user_id),end=expiry, roleIds=active_roles):
    #                                     # Remove from counter
    #                                     if jail_manager.remove_from_counter(discord_id=int(user_id)):
                                            
    #                                         # Send message
    #                                         jailed_info = discord.Embed(title='__You have been jailed!__',
    #                                                                     description=' You have been automatically jailed, since you have broken the'
    #                                                                     'communication rules on community 3 times in a row. Next time be more cautious'
    #                                                                     ' on how you communicate',
    #                                                                     color = discord.Color.red())
    #                                         jailed_info.add_field(name=f'Jail time duration:',
    #                                                             value=f'{CONT_JAIL_DURATION} minutes')
    #                                         jailed_info.add_field(name=f'Sentence started @:',
    #                                                             value=f'{start} UTC')
    #                                         jailed_info.add_field(name=f'Sentece end on:',
    #                                                             value=f'{end_date_time_stamp} UTC')
                                            
    #                                         await message.author.send(embed=jailed_info)
    #                                         await message.channel.send(content=':cop:', delete_after = 60)
                                            
    #                                         # Jailing time
    #                                         guild = self.bot.get_guild(id=667607865199951872)
    #                                         # member = guild.get_member(message.author.id)                
    #                                         role = guild.get_role(710429549040500837)
    #                                         await message.author.add_roles(role, reason='Jailed......')       
    #                                         print(Fore.RED + f'User {message.author} has been jailed!!!!')
                                                                                       
    #                                         for role in active_roles:
    #                                             role = guild.get_role(role_id=int(role))  # Get the role
    #                                             await message.author.remove_roles(role, reason='Jail time served')
                                            
    #                             else: 
    #                                 await message.channel.send(content=f'{message.author.mention} You have received your {current_score}. strike. When you reach 3...you will be spanked!', delete_after = 10)
    #                         else:
    #                             jail_manager.apply_user(discord_id=user_id)
    #                             await message.channel.send(content='You have received your first strike. once you reach 3...you will be spanked and thrown to jail where only Animus can save you', delete_after=50)
    #                             await message.delete()
    #                     else:                       
    #                         await message.author.send(content='You have been put in the LaunchPad Prison. Send a DM to an admin to grant you bail, or sit your time out.')
    #                         await message.delete()
    #                 else:
    #                     pass
    #             else:
    #                 pass
    #         else:
    #             pass
    #     else:
    #         pass

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        print('Print guild has deleted role')
        #TODO make checks if the deleted role is in database
        
        
def setup(bot):
    bot.add_cog(AutoFunctions(bot))