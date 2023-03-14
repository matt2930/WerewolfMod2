from discord import app_commands, Interaction, Embed
from werewolf.game import Game
from config import GameStates
from ui import ChannelSelectView, ConfirmationView, RoleModal
from utils import get_game, update_game

import pdb

class WerewolfModGroup(app_commands.Group):

    @app_commands.command(name='create-game', description='Create a New Game of Werewolf')
    @app_commands.checks.has_role('Mod')
    async def create_game(self, interaction: Interaction, num: int):
        """Creates a new Werewolf Game

        Parameters
        -----------
        num: int
            the game number to create
        """

        current_game = get_game(interaction)

        if current_game:
            if current_game.state not in (GameStates.FINISHED, GameStates.NEW):
                raise Exception('Cannot start game when current game is not FINISHED or NEW.')



        if current_game:
            confirmation = ConfirmationView(interaction)

            if not num > current_game.game_num:
                raise ValueError(f'Unable to create Game {num}, as input "num" must be higher than current game: {current_game.game_num}')

            if num > current_game.game_num + 1:
                await interaction.response.send_message(
                    (f'''
You are creating Game {num}, which is more than 1 above the current game (Game {current_game.game_num}).
I suggest you try creating Game {current_game.game_num + 1}.
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
        current_game = Game(game_num=num, guild=interaction.guild)
        select_view = ChannelSelectView(current_game)
        await interaction.response.send_message(f'Select Channels for Game {current_game.game_num}', view=select_view)
        await select_view.wait()

    @app_commands.command(name='open-signups', description='Open Signups for Current Game')
    @app_commands.checks.has_role('Mod')
    async def open_signups(self, interaction: Interaction):
        current_game = get_game(interaction)
        signups_channel_name = await current_game.open_signups()
        update_game(interaction, current_game)
        await interaction.response.send_message(f'Signups started in {signups_channel_name}.')

    @app_commands.command(name='get-current-game-info', description='Show key information about current running game.')
    @app_commands.checks.has_role('Mod')
    async def get_current_game(self, interaction: Interaction):
        current_game = get_game(interaction)

        game_embed = Embed(
            title=f'Game {current_game.game_num}',
            description=f'Game {current_game.game_num} Information'
        )
        game_embed.add_field(name='Current State', value=current_game.state.value)
        if current_game.state == GameStates.IN_PROGRESS_DAY or current_game.state == GameStates.IN_PROGRESS_NIGHT:
            game_embed.add_field(name='Night/Day Cycle', value=current_game.cycle)

        game_embed.add_field(name='Players', value="\n".join([player.member.name for player in current_game.players]), inline=False)
        game_embed.add_field(name='Active Channels', value="\n".join([current_game.channels[channel].name for channel in current_game.channels]), inline=False)

        await interaction.response.send_message(embed=game_embed, ephemeral=True)

    @app_commands.command(name='in-list')
    @app_commands.checks.has_role('Mod')
    async def get_in_list(self, interaction: Interaction):
        current_game = get_game(interaction)
        await interaction.response.send_message(f'Current Players: {current_game.players}')

    @app_commands.command(name='close-signups', description='Close Signups for Current Game')
    @app_commands.checks.has_role('Mod')
    async def close_signups(self, interaction: Interaction):
        current_game = get_game(interaction)
        players = await current_game.close_signups()
        print(players)
        update_game(interaction, current_game)
        await interaction.response.send_message(f'Number of players: {len(players)}')


    @app_commands.command(name='end-game', description='Ends current game and sets all players to Spectators')
    @app_commands.checks.has_role('Mod')
    async def end_game(self, interaction: Interaction):
        current_game = get_game(interaction)
        await interaction.response.send_message(f'Ending Game {current_game.game_num}...')
        await current_game.end_game()
        update_game(interaction, current_game)
        await interaction.followup.send(f'All previously alive/dead players are now spectators.')


    @app_commands.command(name='assign-roles', description='Assign roles to Alive players')
    @app_commands.checks.has_role('Mod')
    async def assign_roles(self, interaction: Interaction):
        current_game = get_game(interaction)
        if current_game.state != GameStates.ASSIGNMENT:
            raise Exception(f'Unable to assign roles unless game is in state: {GameStates.ASSIGNMENT.value}')

        role_modal = RoleModal()
        await interaction.response.send_modal(role_modal)
        await role_modal.wait()

        for i, player in enumerate(current_game.players):
            player.role = role_modal.roles[i]

        current_game.roles = role_modal.roles
        current_game.state = 'ASSIGNED'

        update_game(interaction, current_game)

        role_list_embed = Embed(title='Player Role Assignments')

        player_role_list = ''
        for player in sorted(current_game.players):
            player_role_list = f'{player_role_list}{player.member.name} - {player.role}\n'

        role_list_embed.add_field(name='Player - Role', value=player_role_list)

        print(f'Sending role list: {player_role_list}')
        await role_modal.interaction.response.send_message(embed=role_list_embed)

    @app_commands.command(name='start-game', description='Post Role breakdown, player list, and ')
    @app_commands.checks.has_role('Mod')
    async def start_game(self, interaction: Interaction):
        current_game = get_game(interaction)
        await current_game.start_game()
        update_game(interaction, current_game)
        await interaction.response.send_message('Game Started!')


    @app_commands.command(description='Start game day')
    @app_commands.checks.has_role('Mod')
    async def day(self, interaction: Interaction):
        current_game = get_game(interaction)
        if not current_game.state == GameStates.IN_PROGRESS_NIGHT:
            raise Exception(f'Cannot begin night if game is not in state: {GameStates.IN_PROGRESS_DAY}')
        await current_game.day()
        update_game(interaction, current_game)
        await interaction.response.send_message(f'Started Day {current_game.cycle}')


    @app_commands.command(description='End game day')
    @app_commands.checks.has_role('Mod')
    async def night(self, interaction: Interaction):
        current_game = get_game(interaction)
        if not current_game.state == GameStates.IN_PROGRESS_DAY:
            raise Exception(f'Cannot begin night if game is not in state: {GameStates.IN_PROGRESS_DAY}')
        await current_game.night()
        update_game(interaction, current_game)
        await interaction.response.send_message(f'Started Night {current_game.cycle}')
