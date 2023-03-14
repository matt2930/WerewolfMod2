from werewolf.database.games import GamesDB
from discord import Interaction

def get_game(interaction: Interaction):
    game = GamesDB(interaction.client).get(guild_id=interaction.guild.id)
    print(f'Retrieving game: {game}')
    return game

def update_game(interaction, game):
    return GamesDB(interaction.client).update(game)
