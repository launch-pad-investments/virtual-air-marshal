import os
import sys

import discord
from discord.ext import commands
from discord import Permissions, Colour
from git import Repo, InvalidGitRepositoryError

from utils.jsonReader import Helpers
from .toolsCog.systemMessages import CustomMessages

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)
customMessages = CustomMessages()

helper = Helpers()

bot_setup = helper.read_json_file(file_name='mainBotConfig.json')


def has_access(ctx):
    access_list = bot_setup['userAccess']
    return [user for user in access_list if ctx.message.author.id == user]


def is_public(ctx):
    return ctx.message.channel.type != discord.ChannelType.private


class ManagementCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.check(has_access)
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
    @commands.check(has_access)
    async def remove_user(self, ctx, user: discord.User):
        user_id = int(user.id)
        data = helper.read_json_file(file_name='mainBotConfig.json')
        list_of_user = data['userAccess']
        if user_id in list_of_user:
            list_of_user.remove(user_id)
            if helper.update_json_file(file_name='mainBotConfig.json', key='userAccess', value=list_of_user):
                title = 'Master Access List Updated'
                message = f'You have successfully removed user {user} to master access list'
                await customMessages.system_message(ctx=ctx, color_code=0, message=message, destination=1,
                                                    sys_msg_title=title)
            else:
                title = 'Master Access list update Error'
                message = f'User {user} could not be removed from the list'
                await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                    sys_msg_title=title)
        else:
            title = 'Master Access list update  Error'
            message = f'User {user} could not be removed to the Master Access list'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                sys_msg_title=title)
               
    @commands.command()
    async def remove_role(self, ctx):
        role = discord.utils.get(ctx.guild.roles, name="Jailed")  # Check if role can be found if not than None
        if role:

            print(await role.delete())
        else:
            print('no role found')


    @commands.check(has_access)
    async def reaction_channel_id(self, ctx, channel: discord.TextChannel):
        """
        Function which allows to modify the channel properties where reaction needs to be placed
        :param ctx: Discord Context
        :param channel: discord.TextChannel
        :return:
        """
        channel_id = int(channel.id)
        if helper.update_json_file(file_name='mainBotConfig.json', key='reactionChannelId', value=channel_id):
            title = 'Settings updated'
            message = f'You have successfully applied {channel} with ID {channel_id} to listen for reactions'
            await customMessages.system_message(ctx=ctx, color_code=0, message=message, destination=1,
                                                sys_msg_title=title)
        else:
            title = 'Reaction Channel Modification Error'
            message = 'Channel details could not be updated'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                sys_msg_title=title)

    @commands.command()
    @commands.check(has_access)
    async def reaction_message_id(self, ctx, message_id: int):
        """
        Set the message which script will listen for reactions
        :param ctx:
        :param code:
        :return:
        """

        if helper.update_json_file(file_name='mainBotConfig.json', key='reactionMessageId', value=message_id):
            title = 'Settings updated'
            message = f'You have successfully applied message with ID {message_id} to listen for reactions'
            await customMessages.system_message(ctx=ctx, color_code=0, message=message, destination=1,
                                                sys_msg_title=title)
        else:
            title = 'Reaction Message Modification Error'
            message = 'Message could not be set to listen for reactions'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                sys_msg_title=title)

    @commands.command()
    @commands.check(has_access)
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
