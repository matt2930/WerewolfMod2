import discord

from dataclasses import dataclass
from typing import Optional


from config import GameState, PlayerState
from werewolf.player import Player

@dataclass
class WWGame:
    id: int
    guild: discord.Guild

    def __post_init__(self):
        self.state: GameState = GameState.NEW
        self.channels: dict = dict()
        self.roles = []
        self.players: dict = set()
        self.signups_channel: Optional[discord.TextChannel] = None


    async def create_channels(self, interaction: discord.Interaction):

        if self.state != GameState.NEW:
            await interaction.response.send(f'Game is currently in state: {self.state}. To run channel creation, please start a new game.')
            raise Exception(f'Invalid Game State: {self.state}. Game must be in state "{GameState.NEW}" to create channels')

        self.category_channel = await self.guild.create_category_channel(f'Game {self.id}', position=0)

        for i, channel in enumerate(self.channels):
            self.channels[channel]['channel'] = await self.category_channel.create_text_channel(
                self.channels[channel]['name'],
                position=i,

            )
            # TODO: Set channel perms

        self.state = GameState.READY
        return

    async def open_signups(self):
        if self.state != GameState.READY:
            raise Exception('Unable to open signups')
        print(self.channels)
        self.signups_channel: discord.TextChannel = self.channels['spectator-chat']['channel']
        print(self.signups_channel)
        await self.signups_channel.send(f'Welcome to Game {self.id}! Please type "/wolf join" to sign up.')
        self.state = GameState.SIGNUPS
        return self.signups_channel.name

    async def close_signups(self):
        if self.state != GameState.SIGNUPS:
            raise Exception('Cannot close signups')
        print('closing signups')
        self.state = GameState.PREGAME

        for player in self.players:
            await player.set_state(PlayerState.ALIVE)

        print(self.players)

        return self.players

    async def end_game(self):
        for player in self.players:
            await player.set_state(PlayerState.SPECTATOR)

        self.state = GameState.FINISHED

    async def add_player(self, interaction: discord.Interaction):

        if self.state != GameState.SIGNUPS:
            raise Exception('Unable to join when signups are not active.')

        player = Player(member=interaction.user)
        if player in self.players:
            await interaction.response.send_message('You are already signed up for this game.', ephemeral=True)
            return
        await player.set_state(PlayerState.SIGNED_UP)
        self.players.add(player)
        return

    async def remove_player(self, member: discord.Member):

        if current_game.state != GameState.SIGNUPS:
            raise Exception('Unable to leave when signups are not active.')

        player = Player(member=member)

        if player in self.players:
            self.players.remove(player)

        await player.set_state(PlayerState.SPECTATOR)

        print(self.players)

global current_game
current_game: Optional[WWGame] = None
