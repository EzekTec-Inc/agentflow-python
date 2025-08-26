import asyncio
import os
import sys
import openai
import google.generativeai as genai
from agentflow import Agent, create_node

# Environment variable checks for user-friendliness
if "GEMINI_API_KEY" not in os.environ:
    print("ERROR: GEMINI_API_KEY environment variable is not set.")
    sys.exit(1)
if "OPENAI_API_KEY" not in os.environ:
    print("ERROR: OPENAI_API_KEY environment variable is not set.")
    sys.exit(1)

# Configure Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

async def openai_agent(store):
    prompt = store.get("prompt", "")
    response = await openai.AsyncOpenAI().chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=128,
        temperature=0.7,
    )
    store["response"] = response.choices[0].message.content
    return store

def gemini_agent_sync(store):
    prompt = store.get("prompt", "")
    try:
        model = genai.GenerativeModel("models/gemini-1.5-pro")
        response = model.generate_content(prompt)
        store["response"] = response.text
        return store
    except Exception as e:
        print("Gemini agent error:", e)
        raise

async def gemini_agent(store):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, gemini_agent_sync, store)

async def main():
    # OpenAI agent
    store1 = {"prompt": "Write a concise and summarized ode to ai in shakespeare"}
    agent1 = Agent(create_node(openai_agent))
    result1 = await agent1.decide(store1.copy())
    print("[OpenAI response]:\n", result1["response"])

    # Gemini agent
    store2 = {"prompt": "Summarize the importance of async programming in Python."}
    agent2 = Agent(create_node(gemini_agent))
    result2 = await agent2.decide(store2.copy())
    print("[Gemini response]:\n", result2["response"])

if __name__ == "__main__":
    asyncio.run(main())
