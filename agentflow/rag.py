from .node import Node, SharedStore

class Rag(Node):
    def __init__(self, retriever: Node, generator: Node):
        self.retriever = retriever
        self.generator = generator

    async def call(self, store: SharedStore) -> SharedStore:
        store = await self.retriever.call(store)
        store = await self.generator.call(store)
        return store
