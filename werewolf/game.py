import discord

from dataclasses import dataclass, field
from typing import Optional

from config import GameStates, CHANNEL_CONFIG
from werewolf.player import Player


@dataclass
class Game:
    guild: discord.Guild
    game_num: int
    _state: str = 'NEW'
    category_channel: Optional[discord.CategoryChannel] = None
    channels: dict[str, discord.TextChannel] = field(default_factory=dict)
    roles: list[str] = field(default_factory=list)
    players: set = field(default_factory=set)
    cycle: int = 1

    @property
    def state(self):
        return GameStates[self._state]

    @state.setter
    def state(self, new_state):
        self._state = new_state

    @classmethod
    def from_mongo(cls, client: discord.Client, data: dict):
        guild: discord.Guild = client.get_guild(data['guild'])

        category_channel = None
        channels = {}
        players = set()

        if (category_id := data.get('category_channel')):
            category_channel = guild.get_channel(category_id)

        if len(data.get('channels', {})) > 0:
            for channel_type, channel_id in data.get('channels').items():
                channels[channel_type] = guild.get_channel(channel_id)

        if len(data.get('players', {})) > 0:
            players_data = data.get('players')
            for user_id in players_data:
                if not (member := guild.get_member(int(user_id))):
                    raise RuntimeError(f'Cound not get member object for user: {user_id}')
                player = Player(member, role=players_data[user_id].get('role', ''))
                players.add(player)

        return cls(
            guild=guild,
            game_num=data['game_num'],
            _state=data['_state'],
            category_channel=category_channel,
            channels=channels,
            roles=data.get('roles', []),
            players=players,
            cycle=data['cycle']
        )

    def to_mongo(self):
        _dict = self.__dict__.copy()

        print(f'to_mongo_dict: {_dict}')

        for channel_type, channel in self.channels.items():
            _dict['channels'][channel_type] = channel.id

        _dict['players'] = {}
        for player in self.players:
            _dict['players'][str(player.member.id)] = {'role': player.role}

        _dict['guild'] = self.guild.id
        _dict['category_channel'] = self.category_channel.id

        return _dict

    async def create_channels(self, interaction: discord.Interaction):

        if self.state != GameStates.NEW:
            await interaction.response.send(f'Game is currently in state: {self.state}. To run channel creation, please start a new game.')
            raise Exception(f'Invalid Game State: {self.state}. Game must be in state "{GameStates.NEW}" to create channels')

        self.category_channel = await self.guild.create_category_channel(f'Game {self.game_num}', position=0)

        for i, channel in enumerate(self.channels):
            self.channels[channel] = await self.category_channel.create_text_channel(
                f'g{self.game_num}-{channel}',
                position=i,
            )
            # TODO: Set channel perms
            if channel in CHANNEL_CONFIG[self.state]:
                for role, perms in CHANNEL_CONFIG[self.state][channel].items():
                    if role in ('Alive', 'Dead', 'Spectator', 'Signed Up'):
                        await self.channels[channel].set_permissions(
                            discord.utils.get(self.member.guild.roles, name=role),
                            overwrite=perms
                        )


        self.state = 'READY'
        return

    async def open_signups(self):
        if self.state != GameStates.READY:
            raise Exception('Unable to open signups unless game is in READY state.')

        signups_channel: discord.TextChannel = self.channels['spectator-chat']
        journals_category = discord.utils.get(self.guild.channels, name='Journals')
        if not journals_category:
            await self.guild.create_category_channel('Journals')
        embed = discord.Embed(
            title=f'Welcome to Game {self.game_num}! Please type"/wolf join" to sign up.',
            description='List of currently signed up players.'
        )
        embed.add_field(
            name='Players',
            value=''
        )
        message = await signups_channel.send(embed=embed)
        await message.pin()
        self.state = 'SIGNUPS'
        return signups_channel.name

    async def close_signups(self):
        if self.state != GameStates.SIGNUPS:
            raise Exception('Cannot close signups')
        print('closing signups')
        self.state = 'PREGAME'
        await self.channels['spectator-chat'].edit(name=f'g{self.game_num}-dead-chat')

        for player in self.players:
            await player.update_state('Alive')

        print(self.players)

        return self.players

    async def end_game(self):
        for player in self.players:
            await player.update_state('Spectator')

        self.state = 'FINISHED'

    async def add_player(self, interaction: discord.Interaction):

        if self.state != GameStates.SIGNUPS:
            raise Exception('Unable to join when signups are not active.')

        player = Player(member=interaction.user)
        await player.create_journal()

        if player in self.players:
            await interaction.response.send_message('You are already signed up for this game.', ephemeral=True)
            return False

        await player.update_state('Signed Up')
        self.players.add(player)
        return True

    async def remove_player(self, member: discord.Member):

        if self.state != GameStates.SIGNUPS:
            raise Exception('Unable to leave when signups are not active.')

        player = Player(member=member)

        if player in self.players:
            self.players.remove(player)

        await player.update_state('Spectator')

        print(self.players)

    async def start_game(self):
        for player in self.players:
            journal = player.journal
            await player.update_state('Alive')
            await journal.send(f'You are a {player.role}')

        self.state = 'IN_PROGRESS_NIGHT'


    async def day(self):
        # set vb to allow activity

        # set state to day
        self.state = 'IN_PROGRESS_DAY'

    async def night(self):
        # set vb to read-only

        self.state = 'IN_PROGRESS_NIGHT'
        self.cycle += 1
