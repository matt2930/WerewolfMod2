import discord
import os

from enum import Enum

CURRENT_GAME_CACHE = os.path.join(os.path.expanduser('~'), '.werewolf/current_game.json')

class GameState(Enum):
    NEW = 'setup'
    READY = 'ready'
    SIGNUPS = 'signups'
    PREGAME = 'assigning roles'
    IN_PROGRESS_DAY = 'in progress - DAY'
    IN_PROGRESS_NIGHT = 'in progress - NIGHT'
    FINISHED = 'finished'

class Alignment(Enum):
    TOWN = 1
    WOLF = 2
    NEUTRAL = 3

class PlayerState(Enum):
    ALIVE = 'Alive'
    DEAD = 'Dead'
    SIGNED_UP = 'Signed Up'
    SPECTATOR = 'Spectator'

CHANNEL_CONFIG = {

    GameState.NEW: {
        'breakdown': {

            PlayerState.ALIVE: discord.PermissionOverwrite(send_messages=False, read_messages=True),
            PlayerState.DEAD: discord.PermissionOverwrite(send_messages=False, read_messages=True),
            PlayerState.SIGNED_UP: discord.PermissionOverwrite(send_messages=False, read_messages=True),
            PlayerState.SPECTATOR: discord.PermissionOverwrite(send_messages=False, read_messages=True)
        },
        'results': {

            PlayerState.ALIVE: discord.PermissionOverwrite(send_messages=False, read_messages=True),
            PlayerState.DEAD: discord.PermissionOverwrite(send_messages=False, read_messages=True),
            PlayerState.SIGNED_UP: discord.PermissionOverwrite(send_messages=False, read_messages=True),
            PlayerState.SPECTATOR: discord.PermissionOverwrite(send_messages=False, read_messages=True)
        },
        'townsquare': {

            PlayerState.ALIVE: discord.PermissionOverwrite(send_messages=True, read_messages=True),
            PlayerState.DEAD: discord.PermissionOverwrite(send_messages=False, read_messages=True),
            PlayerState.SIGNED_UP: discord.PermissionOverwrite(send_messages=False, read_messages=True),
            PlayerState.SPECTATOR: discord.PermissionOverwrite(send_messages=False, read_messages=True)
        },
        'voting-booth': {
            PlayerState.ALIVE: discord.PermissionOverwrite(send_messages=False, read_messages=True),
            PlayerState.DEAD: discord.PermissionOverwrite(send_messages=False, read_messages=True),
            PlayerState.SIGNED_UP: discord.PermissionOverwrite(send_messages=False, read_messages=True),
            PlayerState.SPECTATOR: discord.PermissionOverwrite(send_messages=False, read_messages=True)
        },
        'memos': {
            PlayerState.ALIVE: discord.PermissionOverwrite(send_messages=False, read_messages=True),
            PlayerState.DEAD: discord.PermissionOverwrite(send_messages=False, read_messages=True),
            PlayerState.SIGNED_UP: discord.PermissionOverwrite(send_messages=False, read_messages=True),
            PlayerState.SPECTATOR: discord.PermissionOverwrite(send_messages=False, read_messages=True)
        },
        'couple-chat': {
            PlayerState.ALIVE: discord.PermissionOverwrite(send_messages=False, read_messages=False),
            PlayerState.DEAD: discord.PermissionOverwrite(send_messages=False, read_messages=True),
            PlayerState.SIGNED_UP: discord.PermissionOverwrite(send_messages=False, read_messages=False),
            PlayerState.SPECTATOR: discord.PermissionOverwrite(send_messages=False, read_messages=False)
        },
        'wolf-chat': {
            PlayerState.ALIVE: discord.PermissionOverwrite(send_messages=False, read_messages=False),
            PlayerState.DEAD: discord.PermissionOverwrite(send_messages=False, read_messages=False),
            PlayerState.SIGNED_UP: discord.PermissionOverwrite(send_messages=False, read_messages=False),
            PlayerState.SPECTATOR: discord.PermissionOverwrite(send_messages=False, read_messages=False)
        },
        'spectator-chat': {
            PlayerState.ALIVE: discord.PermissionOverwrite(send_messages=False, read_messages=False),
            PlayerState.DEAD: discord.PermissionOverwrite(send_messages=True, read_messages=True),
            PlayerState.SIGNED_UP: discord.PermissionOverwrite(send_messages=True, read_messages=True),
            PlayerState.SPECTATOR: discord.PermissionOverwrite(send_messages=True, read_messages=True)
        }
    },

    GameState.IN_PROGRESS_DAY: {
        'townsquare': {
            PlayerState.ALIVE: discord.PermissionOverwrite(send_messages=True, read_messages=True),
        },
        'voting-booth': {
            PlayerState.ALIVE: discord.PermissionOverwrite(send_messages=True, read_messages=True)
        },
        'memos': {
            PlayerState.ALIVE: discord.PermissionOverwrite(send_messages=True, read_messages=True)
        },
        'couple-chat': {
            PlayerState.SPECTATOR: discord.PermissionOverwrite(send_messages=False, read_messages=True)
        },
        'wolf-chat': {
            PlayerState.SPECTATOR: discord.PermissionOverwrite(send_messages=False, read_messages=True)
        }
    },

    GameState.IN_PROGRESS_NIGHT: {
        'voting-booth': {
            PlayerState.ALIVE: discord.PermissionOverwrite(send_messages=False, read_messages=True)
        }
    }



}
