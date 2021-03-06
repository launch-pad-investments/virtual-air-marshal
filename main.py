"""
Main bot script
"""
import discord
from discord import Intents

from datetime import datetime
import time
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from backoffice.jailManagementDb import JailManagement
from backoffice.vamBackgroundCHecker import BotStructureCheck
from utils.jsonReader import Helpers
from colorama import Fore, Style, init

init(autoreset=True)

jail_manager = JailManagement()
helper = Helpers()
scheduler = AsyncIOScheduler()

bot_setup = helper.read_json_file(file_name='mainBotConfig.json')
bot = commands.Bot(command_prefix=commands.when_mentioned_or(bot_setup['command']), intents=Intents.all())
bot.remove_command('help')
extensions = ['cogs.adminCogs',
              'cogs.autoCogs',
              'cogs.comOwnerCogs',
              'cogs.jailHandlerCogs',
              'cogs.managementCmd',
              'cogs.spamHandlerCogs',
              'cogs.supportHandlerCog',
              'cogs.loggerAutoSystem',
              'cogs.loggerHandlerCogs',
              'cogs.supportTicketCogs',
              'cogs.vamSupportCogs',
              'cogs.helperCogs']

# 'cogs.projectsAdminsCogs'


async def jail_sentence_checker():
    """
    Function to check jailed users for expired jail times
    """
    now = datetime.utcnow().timestamp()  # Gets current time of the system in unix format
    time_of_release = datetime.utcnow()
    overdue_members = jail_manager.get_served_users(timestamp=int(now))  # Gets all overdue members from database
    print(
        Fore.LIGHTMAGENTA_EX + f"============================\nChecking global jail status @ {time_of_release}\n============================")
    if overdue_members:
        print(Fore.LIGHTYELLOW_EX + f'{len(overdue_members)} members served sentence')
        time_of_release = datetime.utcnow()

        for unjailed in overdue_members:
            user_id = unjailed["userId"]
            all_role_ids = unjailed["roleIds"]
            guild_id = unjailed["community"]

            if jail_manager.remove_from_jailed(discord_id=user_id):
                # send notifcation
                dest = await bot.fetch_user(user_id=int(user_id))
                free = discord.Embed(title='__Jail message__',
                                     color=discord.Color.green())
                free.set_thumbnail(url=bot.user.avatar_url)
                free.add_field(name='Message',
                               value='You have been unjailed and you can start to communicate again! '
                                     ' Next time be more caucious what and how you write. Bad behaviour will'
                                     ' not be tolerated')
                await dest.send(embed=free)

                # get guild and member
                guild = bot.get_guild(id=int(guild_id))
                member = guild.get_member(user_id)

                # Check if member still exists
                if member in guild.members:
                    # Give him back roles
                    for taken_role in all_role_ids:
                        to_give = guild.get_role(role_id=int(taken_role))
                        if to_give:
                            await member.add_roles(to_give, reason='Returning back roles')

                            # role = guild.get_role(role_id=710429549040500837)  # Get the jail role
                    role_rmw = discord.utils.get(guild.roles, name="Jailed")

                    if role_rmw:
                        if role_rmw in member.roles:
                            await member.remove_roles(role_rmw, reason='Jail time served')

                    print(
                        Fore.LIGHTGREEN_EX + f"{member} Successfully released from jail on {guild} and state restored ")
                else:
                    print(Fore.LIGHTRED_EX + f'Member {member} is not on {guild} anymore')
        print(Fore.LIGHTYELLOW_EX + f'@{time_of_release} --> {len(overdue_members)} members have been unjailed!')
    else:
        print(Fore.LIGHTYELLOW_EX + f'Non of members served sentence yet')
    return


def start_scheduler():
    """
    Starting scheduler for functions
    """
    scheduler.add_job(jail_sentence_checker, CronTrigger(second="00"))
    scheduler.start()


if __name__ == '__main__':
    print(Fore.YELLOW + 'Checking VAM Integrity on start')
    BotStructureCheck().check_collections()

    print(Fore.YELLOW + 'Loading extensions')
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
    start_scheduler()
    bot.run(bot_setup['token'], reconnect=True)


