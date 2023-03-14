import discord

from werewolf.database import db, MongoABC
from werewolf.player import Player

class PlayersDB(MongoABC):

    @property
    def collection(self):
        return db.players

    def __init__(self, client: discord.Client):
        self.client = client

    def get(self, user_id: int, guild_id: int):

        data = self.collection.find_one({'user_id': user_id, 'guild_id': guild_id})

        if not data:
            return

        return Player.from_mongo(
            client=self.client,
            data=data
        )

    def create(self, player: Player):
        return self.collection.insert_one(player.as_dict())

    def update(self, player: Player):
        self.collection.replace_one(
            {'user_id': player.member.id, 'guild_id': player.member.guild.id},
            player.to_mongo()
        )
