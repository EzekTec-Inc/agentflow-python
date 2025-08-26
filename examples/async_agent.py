import asyncio
import os
import sys
import openai
import google.generativeai as genai
from agentflow import Agent, create_node

if "GEMINI_API_KEY" not in os.environ:
    print("ERROR: GEMINI_API_KEY environment variable is not set.")
    sys.exit(1)
if "OPENAI_API_KEY" not in os.environ:
    print("ERROR: OPENAI_API_KEY environment variable is not set.")
    sys.exit(1)

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

async def openai_agent(store):
    prompt = store.get("prompt", "")
    response = await openai.AsyncOpenAI().chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=64,
        temperature=0.7,
    )
    store["response"] = response.choices[0].message.content
    return store

def gemini_agent_sync(store):
    prompt = store.get("prompt", "")
    model = genai.GenerativeModel("models/gemini-1.5-pro")
    response = model.generate_content(prompt)
    store["response"] = response.text
    return store

async def gemini_agent(store):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, gemini_agent_sync, store)

async def main():
    store1 = {"prompt": "Write a haiku about async Rust."}
    store2 = {"prompt": "Summarize the benefits of concurrency."}

    agent1 = Agent(create_node(openai_agent))
    agent2 = Agent(create_node(gemini_agent))

    print(f"Agent 1 (OpenAI) prompt: {store1['prompt']}\n")
    print(f"Agent 2 (Gemini) prompt: {store2['prompt']}\n")
    print("="*68 + "\n")

    fut1 = agent1.decide(store1)
    fut2 = agent2.decide(store2)
    result1, result2 = await asyncio.gather(fut1, fut2)

    print(f"Agent 1 (OpenAI) response:\n{result1['response']}\n")
    print(f"Agent 2 (Gemini) response:\n{result2['response']}\n")

if __name__ == "__main__":
    asyncio.run(main())
