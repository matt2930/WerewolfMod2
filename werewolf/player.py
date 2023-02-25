import discord

from config import PlayerState
from dataclasses import dataclass, field

@dataclass
class WWRole:
    name: str
    type: str
    alignment: str
    night_action: bool

@dataclass
class Player:
    member: discord.Member
    _state: PlayerState = None
    role: WWRole = field(default_factory=list)

    def __hash__(self):
        return hash((self.member,))

    def __eq__(self, other):
        return self.member == other.member

    async def clear_roles(self):
        print('Clearing roles')
        roles = self.member.roles
        if len(roles) > 1:
            roles = roles[1:]
            await self.member.remove_roles(*roles)

    async def set_state(self, state: PlayerState):
        await self.clear_roles()
        print(f'Adding Role: {state.value}')
        await self.member.add_roles(discord.utils.get(self.member.guild.roles, name=state.value))
        self._state = state

    async def vote(self):
        pass

    async def submit(self):
        pass
