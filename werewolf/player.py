import asyncio
import discord
import yaml
from pathlib import Path
from config import PlayerStates
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Role:
    name: str
    type: str
    alignment: str
    night_action: bool
    charges: int = 0

    def __hash__(self):
        return hash((self.name,))

roles_by_name = {}
with open((Path(__file__).parent / 'roles/roles.yml').resolve()) as f:
    all_roles = yaml.safe_load(f)
    for alignment in all_roles:
        for name, config in all_roles[alignment].items():
            roles_by_name[name] = Role(
                    name=name,
                    type='tmp',
                    alignment=alignment,
                    night_action=config['night_action']
                )


@dataclass
class Player:
    member: discord.Member
    role: str = ''

    @property
    def journal(self):
        journal = discord.utils.get(self.member.guild.channels, name=f'{self.member.name}-journal')
        if not journal:
            journal = self.create_journal()
        return journal

    def __eq__(self, other):
        return self.member == other.member


    def __hash__(self):
        return self.member.id

    async def create_journal(self):
        journals_category = discord.utils.get(self.member.guild.channels, name='Journals')

        journal = discord.utils.get(self.member.guild.channels, name=f'{self.member.name}-journal')

        if not journal:
            await journals_category.create_text_channel(
                f'{self.member.name}-journal',
                overwrites={
                    self.member: discord.PermissionOverwrite(send_messages=True),
                    discord.utils.get(self.member.guild.roles, name='Spectator'): discord.PermissionOverwrite(read_messages=True)
                }
            )

        return journal

    async def clear_roles(self):
        print('Clearing Roles...')
        roles = [role for role in self.member.roles if role.name not in ('@everyone', 'Mod')]
        print(f'roles:{roles}')
        if len(roles) >= 1:
            await self.member.remove_roles(*roles)

    async def update_state(self, state: str):
        await self.clear_roles()
        print (f'Adding role: {state}')
        print(f'Possible Roles: {self.member.guild.roles}')
        await self.member.add_roles(discord.utils.get(self.member.guild.roles, name=state))

    async def set_role(self, role_name: str):
        self.role = roles_by_name[role_name.lower().replace(' ', '_')]

    async def vote(self, other, game):
        # Check if player is alive:
        other_player = Player(member=other)
        if other_player not in game.players:

            return False

    async def submit(self):
        pass
