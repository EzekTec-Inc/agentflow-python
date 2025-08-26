import asyncio
import os
import sys
import openai
import google.generativeai as genai
from agentflow import Rag, create_node

if "GEMINI_API_KEY" not in os.environ:
    print("ERROR: GEMINI_API_KEY environment variable is not set.")
    sys.exit(1)
if "OPENAI_API_KEY" not in os.environ:
    print("ERROR: OPENAI_API_KEY environment variable is not set.")
    sys.exit(1)

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

async def retriever(store):
    query = store.get("query", "")
    response = await openai.AsyncOpenAI().chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Retrieve context for: {query}"}],
        max_tokens=64,
        temperature=0.7,
    )
    store["context"] = response.choices[0].message.content
    return store

def generator_sync(store):
    context = store.get("context", "")
    model = genai.GenerativeModel("models/gemini-2.5-pro")
    response = model.generate_content(f"Generate a summary for: {context}")
    store["response"] = response.text
    return store

async def generator(store):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, generator_sync, store)

async def main():
    rag = Rag(create_node(retriever), create_node(generator))
    store = {"query": "The color of the sky is blue."}
    result = await rag.call(store)
    print(result["response"])

if __name__ == "__main__":
    asyncio.run(main())
