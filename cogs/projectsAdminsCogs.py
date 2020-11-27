import asyncio
import os.path
import random
import sys

from captcha.image import ImageCaptcha
from discord import File, Embed
from discord.ext import commands

from cogs.toolsCog.systemMessages import CustomMessages
from utils.jsonReader import Helpers

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)
print(project_path)

helper = Helpers()
customMessages = CustomMessages()
bot_setup = helper.read_json_file(file_name='mainBotConfig.json')


def check(author):
    def inner_check(message):
        """
        Check for answering the verification message on withdrawal. Author origin
        """
        if message.author.id == author.id:
            return True
        else:
            return False

    return inner_check


class ProjectAdmins(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bag_of_words = ['animus', 'crypto', 'link', 'funny']

    @commands.command()
    async def captcha_test(self, ctx):
        image = ImageCaptcha(width=280, height=90)
        rand_word = random.choice(self.bag_of_words)
        user_id = f'{ctx.author.id}'

        image.generate(rand_word)
        image.write(chars=rand_word, output=f'./captchapictures/{user_id}.png', format='png')
        file_path = project_path + f'/captchapictures/{user_id}.png'
        img = File(fp=file_path)
        await ctx.channel.send(file=img, content='You have 60 seconds time to resolve captcha')

        try:
            msg_usr = await self.bot.wait_for('message', check=check(ctx.message.author), timeout=60.0)

            if msg_usr.content == rand_word:
                await ctx.author.send(content='Great you are not a robot')
            else:
                await ctx.author.send(content="Captcha Verification Failed. Please try again by starting all over with"
                                              " @VirtualMarshal again")
        except asyncio.TimeoutError:
            await ctx.author.send(content='Your time has run out please request captcha again with command recaptcha')

    @commands.command()
    async def request_new(self):
        pass


def setup(bot):
    bot.add_cog(ProjectAdmins(bot))
