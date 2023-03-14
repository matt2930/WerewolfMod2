from discord import app_commands, Interaction, Member
from config import GameStates
from utils import get_game, update_game
from werewolf.game import Game
from ui import ConfirmationView

def is_signups():
    def predicate(interaction: Interaction) -> bool:
        current_game = get_game(interaction)
        if current_game.state == GameStates.SIGNUPS and interaction.channel.name == current_game.channels['spectator-chat'].name:
            return True
        return False
    return app_commands.check(predicate)


def can_vote():
    def predicate(interaction: Interaction) -> bool:
        current_game = get_game(interaction)
        return current_game.state == GameStates.IN_PROGRESS_DAY \
                and interaction.channel == current_game.channels['voting-booth']
    return app_commands.check(predicate)


class WerewolfPlayerGroup(app_commands.Group):

    @app_commands.command(description='Join the current game.')
    @app_commands.checks.has_role('Spectator')
    @is_signups()
    async def join(self, interaction: Interaction):
        current_game = get_game(interaction)
        print(f'User joining: {interaction.user.id}')
        success = await current_game.add_player(interaction)
        if success:
            print(current_game.players)
            update_game(interaction, current_game)
            await interaction.response.send_message(f'You are now signed up for Game {current_game.game_num}', ephemeral=True)

    @app_commands.command(description='Leave the current game.')
    @app_commands.checks.has_role('Signed Up')
    @is_signups()
    async def leave(self, interaction: Interaction):
        current_game = get_game(interaction)
        confirmation = ConfirmationView(interaction)

        await interaction.response.send_message('Are you sure you want to leave this game?', view=confirmation, ephemeral=True)

        timed_out = await confirmation.wait()
        if not timed_out and confirmation.confirm:
            await current_game.remove_player(interaction.user)
            update_game(confirmation.interaction, current_game)
            await confirmation.interaction.response.send_message('You have left the game successfully.', ephemeral=True)

    @app_commands.command(description='Vote for a player')
    @app_commands.checks.has_role('Alive')
    @can_vote()
    async def vote(self, interaction: Interaction, user: Member):
        current_game = get_game(interaction)
        """Votes for a player in the game

        Parameters
        -----------
        user: discord.Member
            the user to vote for
        """
        pass
