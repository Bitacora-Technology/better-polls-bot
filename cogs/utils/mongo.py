import motor.motor_asyncio as motor
from typing import Optional

client = motor.AsyncIOMotorClient('mongodb://localhost:27017')
db = client['better-polls']


class Poll:
    def __init__(self, message: int = None) -> None:
        self.polls = db['polls']
        self.query = {'_id': message}

    async def create(self, query: dict) -> None:
        await self.polls.insert_one(query)

    async def check(self) -> Optional[dict]:
        return await self.polls.find_one(self.query)

    async def update(self, query: dict) -> None:
        set_query = {'$set': query}
        await self.polls.update_one(self.query, set_query, upsert=True)
