import asyncio
from typing import List
from .node import Node, SharedStore

class MultiAgent(Node):
    def __init__(self, agents: List[Node]):
        self.agents = agents

    async def call(self, store: SharedStore) -> SharedStore:
        await asyncio.gather(*(agent.call(store) for agent in self.agents))
        return store
