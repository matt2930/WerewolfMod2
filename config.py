import dotenv
import discord
import os

from enum import Enum

dotenv.load_dotenv()

CURRENT_GAME_CACHE_DIR = os.path.join(os.path.expanduser('~'), '.werewolf')

class GameStates(Enum):
    NEW = 'setup'
    READY = 'ready'
    SIGNUPS = 'signups'
    ASSIGNMENT = 'assigning roles'
    ASSIGNED = 'roles assigned'
    IN_PROGRESS_DAY = 'in progress - DAY'
    IN_PROGRESS_NIGHT = 'in progress - NIGHT'
    FINISHED = 'finished'


class Alignment(Enum):
    TOWN = 1
    WOLF = 2
    NEUTRAL = 3

class PlayerStates(Enum):
    ALIVE = 'Alive'
    DEAD = 'Dead'
    SIGNED_UP = 'Signed Up'
    SPECTATOR = 'Spectator'

CHANNEL_CONFIG = {

    GameStates.NEW: {
        'breakdown': {
            PlayerStates.ALIVE.value: discord.PermissionOverwrite(send_messages=False, read_messages=True),
            PlayerStates.DEAD.value: discord.PermissionOverwrite(send_messages=False, read_messages=True),
            PlayerStates.SIGNED_UP.value: discord.PermissionOverwrite(send_messages=False, read_messages=True),
            PlayerStates.SPECTATOR.value: discord.PermissionOverwrite(send_messages=False, read_messages=True),
            'default': True
        },
        'results': {
            PlayerStates.ALIVE.value: discord.PermissionOverwrite(send_messages=False, read_messages=True),
            PlayerStates.DEAD.value: discord.PermissionOverwrite(send_messages=False, read_messages=True),
            PlayerStates.SIGNED_UP.value: discord.PermissionOverwrite(send_messages=False, read_messages=True),
            PlayerStates.SPECTATOR.value: discord.PermissionOverwrite(send_messages=False, read_messages=True),
            'default': True
        },
        'townsquare': {
            PlayerStates.ALIVE.value: discord.PermissionOverwrite(send_messages=True, read_messages=True),
            PlayerStates.DEAD.value: discord.PermissionOverwrite(send_messages=False, read_messages=True),
            PlayerStates.SIGNED_UP.value: discord.PermissionOverwrite(send_messages=False, read_messages=True),
            PlayerStates.SPECTATOR.value: discord.PermissionOverwrite(send_messages=False, read_messages=True),
            'default': True
        },
        'voting-booth': {
            PlayerStates.ALIVE.value: discord.PermissionOverwrite(send_messages=False, read_messages=True),
            PlayerStates.DEAD.value: discord.PermissionOverwrite(send_messages=False, read_messages=True),
            PlayerStates.SIGNED_UP.value: discord.PermissionOverwrite(send_messages=False, read_messages=True),
            PlayerStates.SPECTATOR.value: discord.PermissionOverwrite(send_messages=False, read_messages=True),
            'default': True
        },
        'memos': {
            PlayerStates.ALIVE.value: discord.PermissionOverwrite(send_messages=False, read_messages=True),
            PlayerStates.DEAD.value: discord.PermissionOverwrite(send_messages=False, read_messages=True),
            PlayerStates.SIGNED_UP.value: discord.PermissionOverwrite(send_messages=False, read_messages=True),
            PlayerStates.SPECTATOR.value: discord.PermissionOverwrite(send_messages=False, read_messages=True),
            'default': True
        },
        'couple-chat': {
            PlayerStates.ALIVE.value: discord.PermissionOverwrite(send_messages=False, read_messages=False),
            PlayerStates.DEAD.value: discord.PermissionOverwrite(send_messages=False, read_messages=True),
            PlayerStates.SIGNED_UP.value: discord.PermissionOverwrite(send_messages=False, read_messages=False),
            PlayerStates.SPECTATOR.value: discord.PermissionOverwrite(send_messages=False, read_messages=False)
        },
        'wolf-chat': {
            PlayerStates.ALIVE.value: discord.PermissionOverwrite(send_messages=False, read_messages=False),
            PlayerStates.DEAD.value: discord.PermissionOverwrite(send_messages=False, read_messages=False),
            PlayerStates.SIGNED_UP.value: discord.PermissionOverwrite(send_messages=False, read_messages=False),
            PlayerStates.SPECTATOR.value: discord.PermissionOverwrite(send_messages=False, read_messages=False),
            'default': True,
        },
        'spectator-chat': {
            PlayerStates.ALIVE.value: discord.PermissionOverwrite(send_messages=False, read_messages=False),
            PlayerStates.DEAD.value: discord.PermissionOverwrite(send_messages=True, read_messages=True),
            PlayerStates.SIGNED_UP.value: discord.PermissionOverwrite(send_messages=True, read_messages=True),
            PlayerStates.SPECTATOR.value: discord.PermissionOverwrite(send_messages=True, read_messages=True),
            'default': True
        }
    },

    GameStates.IN_PROGRESS_DAY: {
        'townsquare': {
            PlayerStates.ALIVE.value: discord.PermissionOverwrite(send_messages=True, read_messages=True),
        },
        'voting-booth': {
            PlayerStates.ALIVE.value: discord.PermissionOverwrite(send_messages=True, read_messages=True)
        },
        'memos': {
            PlayerStates.ALIVE.value: discord.PermissionOverwrite(send_messages=True, read_messages=True)
        },
        'couple-chat': {
            PlayerStates.SPECTATOR.value: discord.PermissionOverwrite(send_messages=False, read_messages=True)
        },
        'wolf-chat': {
            PlayerStates.SPECTATOR.value: discord.PermissionOverwrite(send_messages=False, read_messages=True)
        }
    },

    GameStates.IN_PROGRESS_NIGHT: {
        'voting-booth': {
            PlayerStates.ALIVE.value: discord.PermissionOverwrite(send_messages=False, read_messages=True)
        }
    }
}
