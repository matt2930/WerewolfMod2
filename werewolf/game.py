import discord
import json
import os

from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path

from config import GameState, PlayerState, CURRENT_GAME_CACHE
from werewolf.player import Player

@dataclass
class Game:
    id: int
    guild: discord.Guild
    state: GameState = GameState.NEW
    channels: dict = field(default_factory=dict)
    roles: list = field(default_factory=list)
    players: dict = field(default_factory=dict)
    signups_channel: Optional[discord.TextChannel] = None
    category_channel: Optional[discord.CategoryChannel] = None

    def __post_init__(self):
        if self.players == {}:
            self.players = set()
        else:
            self.players = set(self.players)

    def write_to_file(self, file: str):

        channels = {}
        if len(self.channels) > 0:
            channels = {channel: {'channel_id': config['channel'].id} for channel, config in self.channels.items()}

        players = []
        if self.players != set():
            players = [(player.member.id, player._state.name) for player in self.players]

        signups_channel_id = ''
        if self.signups_channel:
            signups_channel_id = self.signups_channel.id

        category_channel_id = ''
        if self.category_channel:
            category_channel_id = self.category_channel.id


        game_as_dict = dict(
            id=self.id,
            guild_id=self.guild.id,
            state=self.state.name,
            channels=channels,
            roles=self.roles,
            players=players,
            signups_channel_id=signups_channel_id,
            category_channel_id=category_channel_id
        )

        path = Path(file)

        if not os.path.isdir(path.resolve().parent):
            os.mkdir(path.resolve().parent)

        with open(path.resolve(), 'w') as f:
            json.dump(game_as_dict, f)

        return path

    @classmethod
    async def load_from_file(cls, file: str, client: discord.Client):

        path = Path(file)
        if not path.exists():
            raise FileNotFoundError('Unable to find game file')

        with open(path.resolve(), 'r') as f:
            game = json.load(f)

        print(f'Game Data: {game}')

        guild: discord.Guild = await client.fetch_guild(int(game['guild_id']))

        channels = {}
        for channel, config in game.get('channels', {}).items():
            channel_obj = await guild.fetch_channel(config['channel_id'])
            channels[channel] = {'name': channel_obj.name, 'channel': channel_obj}

        players = set()

        for player in game.get('players', []):
            member_id = player[0]
            state = player[1]

            players.add(Player(member=await guild.fetch_member(member_id), _state=PlayerState[state]))

        for player in players:
            await player.set_state(player._state) # re-assign roles from last bot state


        return cls(
            id=game['id'],
            guild=guild,
            state=GameState[game['state']],
            channels=channels,
            roles=game['roles'],
            players=players,
            signups_channel=discord.Object(int(game['signups_channel_id'])) if game['signups_channel_id'] else None,
            category_channel=discord.Object(int(game['category_channel_id'])) if game['category_channel_id'] else None
        )



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

        if self.state != GameState.SIGNUPS:
            raise Exception('Unable to leave when signups are not active.')

        player = Player(member=member)

        if player in self.players:
            self.players.remove(player)

        await player.set_state(PlayerState.SPECTATOR)

        print(self.players)
