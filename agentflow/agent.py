import asyncio
from typing import Dict, Any
from .node import Node, SharedStore
import traceback

class Agent(Node):
    def __init__(self, node: Node, max_retries: int = 1, wait_millis: int = 0):
        self.node = node
        self.max_retries = max_retries
        self.wait_millis = wait_millis

    async def decide(self, input: SharedStore) -> SharedStore:
        last_exc = None
        for _ in range(self.max_retries):
            try:
                return await self.node.call(input)
            except Exception as exc:
                last_exc = exc
                print("Agent exception:", exc)
                traceback.print_exc()
                if self.wait_millis:
                    await asyncio.sleep(self.wait_millis / 1000)
        raise RuntimeError(f"Agent failed after retries: {last_exc}")

    async def call(self, store: SharedStore) -> SharedStore:
        return await self.node.call(store)
