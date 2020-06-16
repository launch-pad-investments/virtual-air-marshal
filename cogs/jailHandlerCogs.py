import os
import sys

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

from datetime import datetime
from datetime import timedelta
import time
import discord
from discord import Member as DiscordMember

from backoffice.jailSystemDb import JailSystemManager
from backoffice.jailManagementDb import JailManagement

from discord.ext import commands
from discord.ext.commands import Greedy
from utils.jsonReader import Helpers
from cogs.toolsCog.systemMessages import CustomMessages
from colorama import Fore
from cogs.toolsCog.checks import is_community_owner, is_overwatch, is_community_registered, is_public

helper = Helpers()
jail_sys_manager = JailSystemManager()
jail_manager = JailManagement()

custom_message = CustomMessages()
bot_setup = helper.read_json_file(file_name='mainBotConfig.json')


class JailService(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.group()
    @commands.check(is_public)
    @commands.check_any(commands.has_guild_permissions(administrator=True),commands.check(is_overwatch), commands.check(is_community_owner), commands.check(is_community_registered))
    async def jail(self, ctx):
        if ctx.invoked_subcommand is None:
            title = '__Available commands under ***Jail*** category!__'
            description = 'Jail system was designed with intentions to keep the language of the community clean and social. If member breaches language for 3 minutes, he/she is sent to jail for 2 minutes.' 
            ' All roles are removed and given back once jail-time has expired.'
            value = [{'name': f'{bot_setup["command"]}jail on',
                      'value': "Turns the jail ON"},
                     {'name': f'{bot_setup["command"]}jail off',
                      'value': "Turns the jail system off"},
                     {'name': f'{bot_setup["command"]}jail release <@discord.User>',
                      'value': "Releases the user from jail before the expiration time. Can be used only by users with special rights"},
                     {'name': f'{bot_setup["command"]}jail punish <@discord.User> <duration in minutes>',
                      'value': "Manually puts user to Jail for N amount of minutes. Can be used only by users with special rights"}
                     ]

            await custom_message.embed_builder(ctx=ctx, title=title, description=description, data=value)
            
    @jail.command()
    @commands.check(is_community_registered)
    async def on(self,ctx):
        try:
            await ctx.message.delete()
        except Exception:
            pass

        if jail_sys_manager.turn_on_off(community_id=int(ctx.message.guild.id),direction=1):
            title='__System Message__'
            message = 'You have turned ON the automatic jail system and profanity monitor successfully. '
            await custom_message.system_message(ctx=ctx, color_code=0, message = message, destination = 1, sys_msg_title=title)
        else:
            message = f'There was a backend error. Please try again later or contact one of the administrators on the community. We apologize for inconvinience'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
    
    @jail.command() 
    @commands.check(is_community_registered)
    async def off(self,ctx):
        try:
            await ctx.message.delete()
        except Exception:
            pass
        
        if jail_sys_manager.turn_on_off(community_id=int(ctx.message.guild.id),direction=0):
                title='__System Message__'
                message = 'You have turned OFF automtic jail system and profanity successfully. Your members can get crazy'
                await custom_message.system_message(ctx=ctx, color_code=0, message = message, destination = 1, sys_msg_title=title)
        else:
            message = f'There was a backend error. Please try again later or contact one of the administrators on the community. We apologize for inconvinience'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)

    @jail.command()
    @commands.check(is_public)
    @commands.check_any(commands.check(is_overwatch), commands.check(is_community_owner))
    async def release(self, ctx, user:DiscordMember):
        # Check if member in jail
        if jail_manager.check_if_jailed(discord_id=user.id):
            user_details = jail_manager.get_jailed_user(discord_id=user.id)
            if user_details:            
                if jail_manager.remove_from_jailed(discord_id=user.id):
                    all_role_ids = user_details["roleIds"]                                    
                    free = discord.Embed(title='__Jail message__',
                                        color=discord.Color.green())
                    free.set_thumbnail(url=self.bot.user.avatar_url)
                    free.add_field(name='Message',
                                value=f'You have been manually unjailed by the {ctx.message.author} on {ctx.message.guild}')
                    await user.send(embed=free)

                    # Check if member still exists
                    for taken_role in all_role_ids:
                        to_give= ctx.message.guild.get_role(role_id=int(taken_role))
                        if to_give:
                            await user.add_roles(to_give, reason='Returning back roles')    
                            
                        role_rmw = discord.utils.get(ctx.guild.roles, name="Jailed")
                    
                    if role_rmw: 
                        if role_rmw in user.roles:
                            await user.remove_roles(role_rmw, reason='Jail time served')
                                
                    print(Fore.LIGHTGREEN_EX + f"{user} Successfully released from jail on {ctx.message.guild} and state restored ")
                    
                    message = f'You have successfully release {user} from the jail, and his pre-jail perks have been returned.'
                    await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
                else:
                    message = f'User {user} could not be unjailed due to system error. Please try again later. '
                    await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
            else:
                message = f'User {user} is not jailed at this moment. '
                await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        else:
            message = f'User {user} is not jailed at this moment. '
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
    
    @jail.command()
    @commands.check(is_public)
    @commands.check_any(commands.check(is_overwatch), commands.check(is_community_owner))
    async def punish(self, ctx, user:DiscordMember, duration:int):
        """
        Punish user and throw him to jail
        """
        print(Fore.GREEN + 'Manual Jail')
        # Current time
        start = datetime.utcnow()
        print(Fore.GREEN + f'@{start}')
        # Set the jail expiration to after N minutes 
        td = timedelta(minutes=int(duration))
        
        # calculate future date
        end = start + td
        expiry = (int(time.mktime(end.timetuple())))
        end_date_time_stamp = datetime.utcfromtimestamp(expiry)
                                            
        # guild = self.bot.get_guild(id=int(message.guild.id))  # Get guild
        active_roles = [role.id for role in user.roles][1:] # Get active roles

            
        #jail user in database
        if jail_manager.throw_to_jail(user_id=user.id,community_id=ctx.guild.id,expiration=expiry,role_ids=active_roles):
            
            # Remove user from active counter database
            if jail_manager.remove_from_counter(discord_id=int(user.id)):
                print('Removed from counter')
                
            # Send message
            jailed_info = discord.Embed(title='__You have been jailed!__',
                                        description=f' You have been manually jailed by {ctx.message.author} on {ctx.guild} for {duration} minutes. Status will be restored once Jail Time Expires.',
                                        color = discord.Color.red())
            jailed_info.set_thumbnail(url=self.bot.user.avatar_url)
            jailed_info.add_field(name=f'Jail time duration:',
                                value=f'{duration} minutes',
                                inline=False)
            jailed_info.add_field(name=f'Sentence started @:',
                                value=f'{start} UTC',
                                inline=False)
            jailed_info.add_field(name=f'Sentece ends on:',
                                value=f'{end_date_time_stamp} UTC',
                                inline=False)
            jailed_info.set_thumbnail(url=self.bot.user.avatar_url)
            await user.send(embed=jailed_info)
            
            # ADD Jailed role to user
            print(Fore.GREEN + 'Getting Jailed role on community')
            role = discord.utils.get(ctx.guild.roles, name="Jailed") 
            await user.add_roles(role, reason='Jailed......')       
            print(Fore.RED + f'User {user} has been jailed!!!!')
            
            print(Fore.GREEN + 'Removing active roles from user')                                         
            for role in active_roles:
                role = ctx.guild.get_role(role_id=int(role))  # Get the role
                await user.remove_roles(role, reason='Jail time served')
                
    @jail.error
    async def jail_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = f'Command is allowed to be executed only on the public channels of the {ctx.message.guild}.'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        elif isinstance(error,commands.CheckAnyFailure):
            message = f'You do not have rights to access this area of {self.bot.user} on {ctx.message.guild}.'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        else:
            dest = await self.bot.fetch_user(user_id=int(360367188432912385))
            await custom_message.bug_messages(ctx=ctx,error=error,destination=dest)
            
    @punish.error
    async def punish_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = f'Command is allowed to be executed only on the public channels of the {ctx.message.guild}.'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        elif isinstance(error,commands.CheckAnyFailure):
            message = f'You do not have rights to access this area of {self.bot.user} on {ctx.message.guild}.'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        elif isinstance(error,commands.BadArgument):
            message = f'Wrong argument provided:\n {error}. Command structure is {bot_setup["command"]} jail punish <@discord.User> <duration in minutes>'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        else:
            dest = await self.bot.fetch_user(user_id=int(360367188432912385))
            await custom_message.bug_messages(ctx=ctx,error=error,destination=dest)
            
    @release.error
    async def release_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = f'Command is allowed to be executed only on the public channels of the {ctx.message.guild}.'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        elif isinstance(error,commands.CheckAnyFailure):
            message = f'You do not have rights to access this area of {self.bot.user} on {ctx.message.guild}.'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        elif isinstance(error,commands.BadArgument):
            message = f'Wrong argument provided:\n {error}. Command structure is {bot_setup["command"]} jail release <@discord.User>'
            await custom_message.system_message(ctx, message=message, color_code=1, destination=1)
        else:
            dest = await self.bot.fetch_user(user_id=int(360367188432912385))
            await custom_message.bug_messages(ctx=ctx,error=error,destination=dest)
                
def setup(bot):
    bot.add_cog(JailService(bot))
