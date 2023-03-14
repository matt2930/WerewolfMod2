import discord

from werewolf.database import db, MongoABC
from werewolf.game import Game

class GamesDB(MongoABC):

    @property
    def collection(self):
        return db.games

    def get(self, guild_id: int):

        data = self.collection.find_one({'guild': guild_id})

        if not data:
            return

        return Game.from_mongo(
            client=self.client,
            data=data
        )

    def create(self, game: Game):
        data = game.to_mongo()
        print(data)
        return self.collection.insert_one(data)

    def update(self, game: Game):

        if not self.get(game.guild.id):
            print('creating new game')
            return self.create(game)

        data = game.to_mongo()
        print(f'Updating game in mongodb: {data}')
        return self.collection.replace_one(
            {'guild': data.get('guild')},
            data
        )
