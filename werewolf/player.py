import discord
import yaml
from pathlib import Path
from config import PlayerState
from dataclasses import dataclass, field

@dataclass
class Role:
    name: str
    type: str
    alignment: str
    night_action: bool
    charges: int = 0

    def __hash__(self):
        return hash((self.name,))

with open((Path(__file__).parent / 'roles/roles.yml').resolve()) as f:
    all_roles = yaml.safe_load(f)
    roles_by_name = set()
    for alignment in all_roles:
        for name, config in all_roles[alignment].items():
            roles_by_name.add(
                Role(
                    name=name,
                    type='tmp',
                    alignment=alignment,
                    night_action=config['night_action']
                )
            )



@dataclass
class Player:
    member: discord.Member
    _state: PlayerState = None
    role: Role = field(default_factory=list)

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

    async def set_role(self, role_name: str):
        self.role = roles_by_name[role_name.lower().replace(' ', '_')]

    async def vote(self, other, game):
        # Check if player is alive:
        other_player = Player(member=other)
        if other_player not in game.players:

            return False



    async def submit(self):
        pass
