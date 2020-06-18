import os
import sys
from colorama import Fore

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)


import discord
from discord.ext import commands
from datetime import datetime, timedelta
import time
from discord import DMChannel, Embed, Colour
from utils.jsonReader import Helpers
from toolsCog.systemMessages import CustomMessages
from backoffice.jailManagementDb import JailManagement
from backoffice.jailSystemDb import JailSystemManager
from backoffice.spamSystemDb import SpamSystemManager
from better_profanity import profanity

jail_manager = JailManagement()
helper = Helpers()
custom_messages = CustomMessages()
spam_sys_mng  = SpamSystemManager()
jail_sys_mng = JailSystemManager()

bot_setup = helper.read_json_file(file_name='mainBotConfig.json')
CONST_JAIL_DURATION = 5

class AutoFunctions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        On member join role handling and spam protection
        :param member:
        :return:
        """
        print(Fore.LIGHTYELLOW_EX+f'{member} joining {member.guild} ')
        if spam_sys_mng.check_community_reg_status(community_id=member.guild.id):
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
        else:
            print(f'Community {member.guild} not registered for spam prevention service')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        print('Member left community... checking if exists in database')
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        dest = self.bot.get_channel(id=int(722048385078788217))
        print('Bot has been invited to new guild')
        
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        #TODO integrate database clearing bt guild id and everything else, inform the channel of vam of bot removal
        print('Guild has kicked out the bot')
    
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, guild):
        print('Guild has deleted channel')
        
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        print('Gets called when guild removes role')
        
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        """
        Waits for reaction to specific message and once user agrees it will automatically sign role to him
        :param reaction: discord.Reaction
        :return: None
        """

        author = reaction.member  # Author of reaction
        guild_id = reaction.member.guild.id  #Guild of reaction
        if spam_sys_mng.check_if_security_activated(community_id=guild_id) == 1:
            details = spam_sys_mng.get_details_of_channel(community_id = reaction.member.guild.id)
            if details:
                if reaction.channel_id == details['appliedChannelId']:
                    if reaction.message_id == details['appliedMessageId']:
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
            else:
                pass
        else:
            pass
            
    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            if not isinstance(message.channel, DMChannel):
                user_id = message.author.id
                if jail_sys_mng.jail_activated(community_id=message.guild.id):  # Check if community has jail activated
                    if message.author.id != messsage.guild.owner_id:
                        if profanity.contains_profanity(message.content):
                            await message.delete()
                            await message.channel.send(f'{message.author.mention} You cant use bad words on {message.guild}!', delete_after=15)
                            if not jail_manager.check_if_in_jail(user_id=int(user_id)):      # If user is not jailed yet
                                if jail_manager.check_if_in_counter(discord_id=user_id):
                                    current_score = jail_manager.increase_count(discord_id=user_id)
                                    if current_score >= 3:
                                        print(Fore.GREEN + 'Someone needs to be jailed')
                                        # Current time
                                        start = datetime.utcnow()
                                        print(Fore.GREEN + f'@{start}')
                                        # Set the jail expiration to after N minutes 
                                        td = timedelta(minutes=int(CONST_JAIL_DURATION))
                                        
                                        # calculate future date
                                        end = start + td
                                        expiry = (int(time.mktime(end.timetuple())))
                                        end_date_time_stamp = datetime.utcfromtimestamp(expiry)
                                                                            
                                        # guild = self.bot.get_guild(id=int(message.guild.id))  # Get guild
                                        active_roles = [role.id for role in message.author.roles][1:] # Get active roles
                                        print(Fore.GREEN + f'Has roles:')
                                        for r in active_roles:
                                            print(Fore.YELLOW + f'@Role: {r}')
                                            
                                        #jail user in database
                                        if jail_manager.throw_to_jail(user_id=message.author.id,community_id=message.guild.id,expiration=expiry,role_ids=active_roles):
                                            # Remove user from active counter database
                                            if jail_manager.remove_from_counter(discord_id=int(user_id)):
                                                
                                                # Send message
                                                jailed_info = discord.Embed(title='__You have been jailed!__',
                                                                            description=f' You have been automatically jailed, since you have broken the'
                                                                            f'communication rules on community {message.guild} 3 times in a row. Next time be more cautious'
                                                                            f' on how you communicate. Status will be restored once Jail Time Expires.',
                                                                            color = discord.Color.red())
                                                jailed_info.add_field(name=f'Jail time duration:',
                                                                    value=f'{CONST_JAIL_DURATION} minutes',
                                                                    inline=False)
                                                jailed_info.add_field(name=f'Sentence started @:',
                                                                    value=f'{start} UTC',
                                                                    inline=False)
                                                jailed_info.add_field(name=f'Sentece ends on:',
                                                                    value=f'{end_date_time_stamp} UTC',
                                                                    inline=False)
                                                jailed_info.set_thumbnail(url=self.bot.user.avatar_url)
                                                await message.author.send(embed=jailed_info)
                                                await message.channel.send(content=':cop:', delete_after = 60)
                                                
                                                                                            # Jailing time

                                                # ADD Jailed role to user
                                                print(Fore.GREEN + 'Getting Jailed role on community')
                                                role = discord.utils.get(message.guild.roles, name="Jailed") 
                                                await message.author.add_roles(role, reason='Jailed......')       
                                                print(Fore.RED + f'User {message.author} has been jailed!!!!')
                                                
                                                print(Fore.GREEN + 'Removing active roles from user')                                         
                                                for role in active_roles:
                                                    role = message.guild.get_role(role_id=int(role))  # Get the role
                                                    await message.author.remove_roles(role, reason='Jail time served')
                                    else:
                                        await message.channel.send(content=f'{message.author.mention} You have received your {current_score}. strike. When you reach 3...you will be jailed for {CONST_JAIL_DURATION}!', delete_after = 10)
                                else:
                                    jail_manager.apply_user(discord_id=user_id)
                                    await message.channel.send(content='You have received your first strike. once you reach 3...you will be spanked and thrown to jail where only Animus can save you', delete_after=50)
                                    await message.delete()
                            else:
                                pass
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
            else:
                pass

    # @commands.Cog.listener()
    # async def on_command_error(self, ctx, error):
    #     try:
    #         await ctx.message.delete()
    #     except Exception:
    #         pass
    #     if isinstance(error, commands.CommandNotFound):
    #         title = 'System Command Error'
    #         message = f':no_entry: Sorry, this command does not exist! Please' \
    #                   f'type `{bot_setup["command"]} help` to check available commands.'
    #         await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
    #                                              sys_msg_title=title)
def setup(bot):
    bot.add_cog(AutoFunctions(bot))