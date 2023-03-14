import discord
import os
import pymongo

from abc import ABC, abstractmethod

client = pymongo.MongoClient(f"mongodb+srv://admin:{os.getenv('MONGO_DB_PASSWORD')}@discord.ptvbnyu.mongodb.net/?retryWrites=true&w=majority")
db = client.werewolf

class MongoABC(ABC):

    def __init__(self, client: discord.Client):
        self.client = client



    @property
    @abstractmethod
    def collection(self):
        pass

    @abstractmethod
    def get(self):
        pass

    @abstractmethod
    def create(self):
        pass

    @abstractmethod
    def update(self):
        pass



# TODO: Add roles
# ROLES = _db.roles
