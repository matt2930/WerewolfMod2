import discord
import dotenv
import os
import signal
import sys
import pickle



from config import CURRENT_GAME_CACHE
from mod_group import WerewolfModGroup
from player_group import WerewolfPlayerGroup
from werewolf.game import WWGame, current_game

from discord import app_commands
from typing import Any

MY_GUILD = discord.Object(1078152598542090293)

class Bot(discord.Client):

    def __init__(self):


        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        global current_game
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('-------')
        mod = WerewolfModGroup(name='mod', description='Run Werewolf Mod Commands')
        player = WerewolfPlayerGroup(name='wolf', description='Run player Werewolf commands.')
        bot.tree.add_command(mod)
        bot.tree.add_command(player)
        bot.tree.copy_global_to(guild=MY_GUILD)
        await bot.tree.sync(guild=MY_GUILD)
        if os.path.exists(CURRENT_GAME_CACHE):
            with open(CURRENT_GAME_CACHE) as f:
                current_game = pickle.load(f)
        else:
            current_game = WWGame(id=0, guild=MY_GUILD)

bot = Bot()

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingRole):
        await interaction.response.send_message(error, ephemeral=True)
        return
    if isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message('Unable to run command.', ephemeral=True)
        return
    await interaction.response.send_message(f'An error occured: {error}')


def signal_handler(sig, frame):
    with open(CURRENT_GAME_CACHE, 'w+') as f:
        pickle.dump(current_game, file=f)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


def main():
    dotenv.load_dotenv()

    bot.run(str(os.getenv('TOKEN')))

if __name__ == '__main__':
    main()
