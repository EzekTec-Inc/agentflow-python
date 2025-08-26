import asyncio
from typing import Any, Dict, Callable, Awaitable

SharedStore = Dict[str, Any]

class Node:
    async def call(self, store: SharedStore) -> SharedStore:
        raise NotImplementedError

class SimpleNode(Node):
    def __init__(self, func: Callable[[SharedStore], Awaitable[SharedStore]]):
        self.func = func

    async def call(self, store: SharedStore) -> SharedStore:
        return await self.func(store)

def create_node(func: Callable[[SharedStore], Awaitable[SharedStore]]) -> Node:
    return SimpleNode(func)
