from sanic import Sanic

from motor import motor_asyncio as motor

from os import getenv


class Backend(Sanic):
    __slots__ = ("db", "dbclient")

    def __init__(self, name: str):
        super().__init__(name)
        self.dbclient = motor.AsyncIOMotorClient(
            f"mongodb+srv://fdc:{getenv('token')}@cluster0.djkwu4l.mongodb.net/" \
            "?retryWrites=true&w=majority"
        )
        self.db = self.dbclient["BlogApi"]

    def get_collection(self, name: str):
        return self.db[name]
