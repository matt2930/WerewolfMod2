import discord
import dotenv
import os
import signal
import sys
import pickle

from pathlib import Path

from config import GameState
from discord import app_commands
from ui import ConfirmationView, ChannelSelectView, RoleModal

from config import Alignment, CURRENT_GAME_CACHE
from werewolf import Game, Player, Role

from discord import app_commands
from typing import Any

import traceback

dotenv.load_dotenv()

if os.getenv('GUILD_ID'):
    MY_GUILD = discord.Object(int(os.getenv('GUILD_ID')))

current_game = None

class WerewolfModGroup(app_commands.Group):

    @app_commands.command(name='create-game', description='Create a New Game of Werewolf')
    @app_commands.checks.has_role('Mod')
    async def create_game(self, interaction: discord.Interaction, num: int):
        """Creates a new Werewolf Game

        Parameters
        -----------
        num: int
            the game number to create
        """

        global current_game

        if current_game.state not in (GameState.FINISHED, GameState.NEW):
            raise Exception('Cannot start game when current game is not FINISHED or NEW.')

        confirmation = ConfirmationView(interaction)

        if current_game:

            if not num > current_game.id:
                raise ValueError(f'Unable to create Game {num}, as input "num" must be higher than current game: {current_game.id}')

            if num > current_game.id + 1:
                await interaction.response.send_message(
                    (f'''
You are creating Game {num}, which is more than 1 above the current game (Game {current_game.id}).
I suggest you try creating Game {current_game.id + 1}.
Continue anyways?'''
                     ),
                    view=confirmation,
                    ephemeral=True
                )
                print('waiting for input...')
                timed_out = await confirmation.wait()
                if timed_out:
                    print('timeout. stopping confirmation')
                    return
                if not confirmation.confirmed:
                    return await confirmation.interaction.response.send_message('Cancelled game creation.', ephemeral=True)
                interaction = confirmation.interaction

        print('continuing...')
        current_game = Game(id=num, guild=interaction.guild)
        select_view = ChannelSelectView(current_game)
        await interaction.response.send_message(f'Select Channels for Game {current_game.id}', view=select_view)
        await select_view.wait()

    @app_commands.command(name='open-signups', description='Open Signups for Current Game')
    @app_commands.checks.has_role('Mod')
    async def open_signups(self, interaction: discord.Interaction):
        signups_channel_name = await current_game.open_signups()
        await interaction.response.send_message(f'Signups started in {signups_channel_name}.')


    @app_commands.command(name='close-signups', description='Close Signups for Current Game')
    @app_commands.checks.has_role('Mod')
    async def close_signups(self, interaction: discord.Interaction):
        players = await current_game.close_signups()
        print(players)
        await interaction.response.send_message(f'Number of players: {len(players)}')


    @app_commands.command(name='end-game', description='Ends current game and sets all players to Spectators')
    async def end_game(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Ending Game {current_game.id}...')
        await current_game.end_game()
        await interaction.followup.send(f'All previously alive/dead players are now spectators.')


    @app_commands.command(name='assign-roles', description='Assign roles to Alive players')
    async def assign_roles(self, interaction: discord.Interaction):
        if current_game.state != GameState.PREGAME:
            raise Exception(f'Unable to assign roles unless game is in state: {GameState.PREGAME.value}')

        role_modal = RoleModal()
        await interaction.response.send_modal(role_modal)
        await role_modal.wait()
        print(role_modal.roles)

        for i, player in enumerate(current_game.players):
            player.set_role(role_modal.roles[i])


def is_signups():
    def predicate(interaction: discord.Interaction) -> bool:
        if current_game.state == GameState.SIGNUPS and interaction.channel == current_game.signups_channel:
            return True
        return False
    return app_commands.check(predicate)


def can_vote():
    def predicate(interaction: discord.Interaction) -> bool:
        return current_game.state == GameState.IN_PROGRESS_DAY \
                and interaction.channel == current_game.channels['voting-booth']['channel']
    return app_commands.check(predicate)



class WerewolfPlayerGroup(app_commands.Group):

    @app_commands.command(description='Join the current game.')
    @app_commands.checks.has_role('Spectator')
    @is_signups()
    async def join(self, interaction: discord.Interaction):
        await current_game.add_player(interaction)
        print(current_game.players)
        await interaction.response.send_message(f'You are now signed up for Game {current_game.id}', ephemeral=True)

    @app_commands.command(description='Leave the current game.')
    @app_commands.checks.has_role('Signed Up')
    @is_signups()
    async def leave(self, interaction: discord.Interaction):
        confirmation = ConfirmationView(interaction)

        await interaction.response.send_message('Are you sure you want to leave this game?', view=confirmation, ephemeral=True)

        timed_out = await confirmation.wait()
        if not timed_out and confirmation.confirm:
            await current_game.remove_player(interaction.user)
            await confirmation.interaction.response.send_message('You have left the game successfully.', ephemeral=True)

    @app_commands.command(description='Vote for a player')
    @app_commands.checks.has_role('Alive')
    @can_vote()
    async def vote(self, interaction: discord.Interaction, user: discord.Member):
        """Votes for a player in the game

        Parameters
        -----------
        user: discord.Member
            the user to vote for
        """
        pass



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
        if Path(CURRENT_GAME_CACHE).exists():
            try:
                current_game = await Game.load_from_file(CURRENT_GAME_CACHE, self)
            except FileNotFoundError:
                pass

        if not current_game:
            current_game = Game(id=0, guild=MY_GUILD)
        print(f'Current Game: {current_game}')
        mod = WerewolfModGroup(name='mod', description='Run Werewolf Mod Commands')
        player = WerewolfPlayerGroup(name='wolf', description='Run player Werewolf commands.')
        bot.tree.add_command(mod)
        bot.tree.add_command(player)
        bot.tree.copy_global_to(guild=MY_GUILD)
        await bot.tree.sync(guild=MY_GUILD)


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


def signal_handler(sig, frame):


    print(current_game)
    if current_game:
        current_game.write_to_file(CURRENT_GAME_CACHE)

    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def main():

    print('Starting up bot...')
    bot.run(str(os.getenv('TOKEN')))

if __name__ == '__main__':
    main()
