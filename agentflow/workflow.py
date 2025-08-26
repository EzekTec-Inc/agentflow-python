from typing import Dict, Any, Optional
from .node import Node, SharedStore

class Workflow(Node):
    def __init__(self):
        self.steps: Dict[str, Node] = {}
        self.edges: Dict[str, Dict[str, str]] = {}
        self.start_step: Optional[str] = None

    def add_step(self, name: str, node: Node):
        if self.start_step is None:
            self.start_step = name
        self.steps[name] = node
        self.edges.setdefault(name, {})

    def connect(self, from_step: str, to_step: str, action: str = "default"):
        self.edges[from_step][action] = to_step

    async def run(self, store: SharedStore) -> SharedStore:
        current = self.start_step
        while current:
            node = self.steps[current]
            store = await node.call(store)
            action = store.get("action", "default")
            current = self.edges.get(current, {}).get(action)
        store.pop("action", None)
        return store

    async def call(self, store: SharedStore) -> SharedStore:
        return await self.run(store)
