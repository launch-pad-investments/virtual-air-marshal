"""
Main bot script
"""
import discord
from datetime import datetime
import time
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from backoffice.jailManagementDb import JailManagement
from utils.jsonReader import Helpers
from colorama import Fore, Style

jail_manager = JailManagement()
helper = Helpers()
scheduler = AsyncIOScheduler()


bot_setup = helper.read_json_file(file_name='mainBotConfig.json')
bot = commands.Bot(command_prefix=commands.when_mentioned_or(bot_setup['command']))
bot.remove_command('help')
extensions = ['cogs.managementCmd', 'cogs.autoCogs', 'cogs.adminCogs', 'cogs.comOwnerCogs','cogs.jailHandlerCogs', 'cogs.spamHandlerCogs']

async def jail_sentence_checker():
    now = datetime.utcnow().timestamp()  # Gets current time of the system in unix format
    overdue_members = jail_manager.get_served_users(timestamp=int(now))  # Gets all overdue members from database
    if overdue_members:
        time_of_release = datetime.utcnow()
        for unjailed in overdue_members:
            user_id = unjailed["userId"]
            all_role_ids = unjailed["roleIds"]
            
            if jail_manager.remove_from_jailed(discord_id=user_id):
                #send notifcation 
                dest = await bot.fetch_user(user_id=int(user_id))
                free = discord.Embed(title='__Jail message__',
                                     color=discord.Color.green())
                free.set_thumbnail(url=bot.user.avatar_url)
                free.add_field(name='Message',
                               value='You have been unjailed and you can start to communicate again! '
                               ' Next time be more caucious what and how you write. Bad behaviour will'
                               ' not be tolerated')
                await dest.send(embed=free)
                
                #remove role
                               
                # get guild and member
                guild = bot.get_guild(id=667607865199951872)
                member = guild.get_member(user_id)
                

                # Check if member still exists
                if member in guild.members:
                    # Give him back roles
                    for taken_role in all_role_ids:
                        to_give=guild.get_role(role_id=int(taken_role))
                        if to_give:
                            await member.add_roles(to_give, reason='Returning back roles')    
                           
                    role = guild.get_role(role_id=710429549040500837)  # Get the jail role
                    
                    if role: 
                        if role in member.roles:
                            await member.remove_roles(role, reason='Jail time served')
        print(Fore.GREEN + f'@{time_of_release} --> {len(overdue_members)} members have been unjailed!')
    else:
        pass
    
    return 


def start_scheduler():
    scheduler.add_job(jail_sentence_checker, CronTrigger(second="00"))
    scheduler.start()
        
if __name__ == '__main__':
    notification_str = Fore.MAGENTA + '+++++++++++++++++++++++++++++++++++++++\n' \
                       '           LOADING COGS....        \n'
    for extension in extensions:
        try:
            bot.load_extension(extension)
            notification_str += (Fore.GREEN + f'| {extension}\n')
        except Exception as error:
            notification_str += (Fore.RED + f'| {extension} --> {error}\n')
            raise

    notification_str += Fore.MAGENTA + '+++++++++++++++++++++++++++++++++++++++'
    # Discord Token
    print(notification_str)
    print(Style.RESET_ALL)
    start_scheduler()
    bot.run(bot_setup['token'], reconnect=True)


