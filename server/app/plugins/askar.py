import json
from quart import current_app, abort
from aries_askar import Store, error
import time
import uuid
import hashlib


class Askar:
    def __init__(self):
        self.db = "sqlite://app.db"
        # self.key = Store.generate_raw_key(
        #     hashlib.md5(current_app.config[''].encode()).hexdigest()
        # )

    async def provision(self):
        await Store.provision(self.db, "raw", self.key, recreate=False)

    async def open(self):
        return await Store.open(self.db, "raw", self.key)

    async def get_keys(self, category):
        store = await self.open()

    async def fetch(self, category, data_key):
        store = await self.open()
        try:
            async with store.session() as session:
                data = await session.fetch(category, data_key)
            return json.loads(data.value)
        except:
            return None

    async def store(self, category, data_key, data):
        store = await self.open()
        try:
            async with store.session() as session:
                await session.insert(
                    category,
                    data_key,
                    json.dumps(data),
                    {"~plaintag": "a", "enctag": "b"},
                )
        except:
            abort(404, "Could not store record")

    async def update(self, category, data_key, data):
        store = await self.open()
        try:
            async with store.session() as session:
                await session.replace(
                    category,
                    data_key,
                    json.dumps(data),
                    {"~plaintag": "a", "enctag": "b"},
                )
        except:
            abort(404, "Could not update record")
