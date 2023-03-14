import discord
import dotenv
import os


from discord import app_commands

from command_groups import WerewolfModGroup, WerewolfPlayerGroup

from discord import app_commands
from typing import Any

import traceback

dotenv.load_dotenv()

if os.getenv('GUILD_ID'):
    MY_GUILD = discord.Object(int(os.getenv('GUILD_ID')))

class Bot(discord.Client):

    def __init__(self):

        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):

        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('-------')

        mod = WerewolfModGroup(name='mod', description='Run Werewolf Mod Commands')
        player = WerewolfPlayerGroup(name='wolf', description='Run player Werewolf commands.')
        self.tree.add_command(mod)
        self.tree.add_command(player)
        for guild in self.guilds:
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)


bot = Bot()

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingRole):
        await interaction.response.send_message(error, ephemeral=True)
        return
    if isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message('Unable to run command.', ephemeral=True)
        traceback.print_exception(type(error), error, error.__traceback__)
        return
    await interaction.response.send_message(f'An error occured: {error}')
    traceback.print_exception(type(error), error, error.__traceback__)


def main():

    print('Starting up bot...')
    bot.run(str(os.getenv('TOKEN')))

if __name__ == '__main__':
    main()
