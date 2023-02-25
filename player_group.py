import discord

from discord import app_commands

from config import GameState
from werewolf.game import current_game

def is_signups():
    def predicate(interaction: discord.Interaction) -> bool:
        if current_game.state == GameState.SIGNUPS and interaction.channel == current_game.signups_channel:
            return True
        return False
    return app_commands.check(predicate)


class WerewolfPlayerGroup(app_commands.Group):

    @app_commands.command(description='Join the current game.')
    @app_commands.checks.has_role('Spectator')
    @is_signups()
    async def join(self, interaction: discord.Interaction):
        await current_game.add_player(interaction)
        # TODO: Add signed up role
        print(current_game.players)
        await interaction.response.send_message(f'You are now signed up for Game {current_game.id}', ephemeral=True)

    @app_commands.command(description='Leave the current game.')
    @app_commands.checks.has_role('Signed Up')
    @is_signups()
    async def leave(self, interaction: discord.Interaction):
        # TODO: Prompt for confirmation before leaving
        await current_game.remove_player(interaction.user)
        await interaction.response.send_message('You have left the game successfully.', ephemeral=True)

    @app_commands.command(description='Vote for a player')
    @app_commands.checks.has_role('Alive')
    async def vote(self, interaction: discord.Interaction, user: discord.Member):
        """Votes for a player in the game

        Parameters
        -----------
        user: discord.Member
            the user to vote for
        """

        pass
