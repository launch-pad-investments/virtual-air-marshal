import os
import sys

import discord
from discord.ext import commands
from discord import Permissions, Colour
from git import Repo, InvalidGitRepositoryError

from utils.jsonReader import Helpers
from cogs.toolsCog.systemMessages import CustomMessages
from cogs.toolsCog.checks import is_overwatch

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)
customMessages = CustomMessages()

helper = Helpers()

bot_setup = helper.read_json_file(file_name='mainBotConfig.json')


class ManagementCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.check(is_overwatch)
    async def add_user(self, ctx, user: discord.User):
        """
        :param ctx:
        :param user:
        :return:
        """
        user_id = int(user.id)
        data = helper.read_json_file(file_name='mainBotConfig.json')
        list_of_user = data['userAccess']
        list_of_user.append(int(user_id))
        if helper.update_json_file(file_name='mainBotConfig.json', key='userAccess', value=list_of_user):
            title = 'Master Access List Updated'
            message = f'You have successfully added user {user} to master access list'
            await customMessages.system_message(ctx=ctx, color_code=0, message=message, destination=1,
                                                sys_msg_title=title)
        else:
            title = 'Master Access list update  Error'
            message = f'User {user} could not be added to the Master Access list'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                sys_msg_title=title)
               
    @commands.command()
    async def remove_role(self, ctx):
        role = discord.utils.get(ctx.guild.roles, name="Jailed")  # Check if role can be found if not than None
        if role:

            print(await role.delete())
        else:
            print('no role found')


    @commands.command()
    @commands.check(is_overwatch)
    async def update(self, ctx):
        extensions = ['managementCmd', 'autoCogs', 'adminCogs']
        notification_str = ''
        try:
            repo = Repo()  # Initiate repo
            git = repo.git
            git.pull()
            notification_str += 'GIT UPDATE STATUS\n' \
                                ' Latest commits pulled :green_circle: \n' \
                                '=============================================\n'
        except InvalidGitRepositoryError:
            notification_str += f'GIT UPDATE: There has been an error while pulling latest commits :red_circle:  \n' \
                                f'Error: Git Repository could not be found\n' \
                                f'=============================================\n'

        notification_str += 'STATUS OF COGS AFTER RELOAD\n'
        for extension in extensions:
            print(f'Trying to load extension {extension}')
            try:
                self.bot.unload_extension(f'cogs.{extension}')
                self.bot.load_extension(f'cogs.{extension}')
                notification_str += f'{extension} :green_circle:  \n'
                print('success')
                print('=========')
            except Exception as e:
                notification_str += f'{extension} :red_circle:' \
                                    f'Error: {e} \n'
                print('failed')
                print('=========')

        await customMessages.system_message(ctx=ctx, message=notification_str, color_code=0, destination=0)


def setup(bot):
    bot.add_cog(ManagementCommands(bot))
