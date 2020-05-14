"""
Main bot script
"""

import discord
from discord.ext import commands

from utils.jsonReader import Helpers

helper = Helpers()

bot_setup = helper.read_json_file(file_name='mainBotConfig.json')
bot = commands.Bot(command_prefix=commands.when_mentioned_or(bot_setup['command']))
bot.remove_command('help')
extensions = ['cogs.managementCmd', 'cogs.autoCogs', 'cogs.adminCogs']


@bot.event
async def on_ready():
    """
    Print out to console once bot logs in
    :return:
    """
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(f'{bot_setup["command"]} or Tag'))
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


if __name__ == '__main__':
    notification_str = ''
    for extension in extensions:
        try:
            bot.load_extension(extension)
            notification_str += f'{extension} :smile: \n'
        except Exception as error:
            notification_str += f'{extension} --> {error} :angry: \n'
            raise
    print(notification_str)
    # Discord Token
    bot.run(bot_setup['token'])
