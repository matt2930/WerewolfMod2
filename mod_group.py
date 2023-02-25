import discord


from werewolf.game import WWGame, current_game
from config import GameState
from discord import app_commands
from ui import ConfirmationView, ChannelSelectView, RoleModal

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
        current_game = WWGame(id=num, guild=interaction.guild)
        await interaction.response.send_message(f'Select Channels for Game {current_game.id}', view=ChannelSelectView())


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
