import asyncio
import os
import sys
import openai
import google.generativeai as genai
from agentflow import MultiAgent, create_node

if "GEMINI_API_KEY" not in os.environ:
    print("ERROR: GEMINI_API_KEY environment variable is not set.")
    sys.exit(1)
if "OPENAI_API_KEY" not in os.environ:
    print("ERROR: OPENAI_API_KEY environment variable is not set.")
    sys.exit(1)

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

async def agent1(store):
    prompt = "TypeScript game logic for Space Invader"
    response = await openai.AsyncOpenAI().chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=128,
        temperature=0.7,
    )
    store["typescript"] = response.choices[0].message.content
    return store

def agent2_sync(store):
    prompt = "HTML structure for Space Invader game"
    model = genai.GenerativeModel("models/gemini-1.5-pro")
    response = model.generate_content(prompt)
    store["html"] = response.text
    return store

async def agent2(store):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, agent2_sync, store)

async def agent3(store):
    prompt = "TailwindCSS styles for Space Invader game"
    response = await openai.AsyncOpenAI().chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=128,
        temperature=0.7,
    )
    store["tailwindcss"] = response.choices[0].message.content
    return store

async def main():
    agents = [
        create_node(agent1),
        create_node(agent2),
        create_node(agent3),
    ]
    multi_agent = MultiAgent(agents)
    store = {}
    result = await multi_agent.call(store)
    print("=== Space Invader Game Artifacts ===\n")
    print("--- TypeScript Game Logic ---\n", result.get("typescript"))
    print("--- HTML Structure ---\n", result.get("html"))
    print("--- TailwindCSS Styles ---\n", result.get("tailwindcss"))

if __name__ == "__main__":
    asyncio.run(main())
