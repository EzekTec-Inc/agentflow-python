from typing import List
from .node import Node, SharedStore

class MapReduce(Node):
    def __init__(self, mapper: Node, reducer: Node):
        self.mapper = mapper
        self.reducer = reducer

    async def call(self, stores: List[SharedStore]) -> SharedStore:
        mapped = [await self.mapper.call(s) for s in stores]
        return await self.reducer.call(mapped)
