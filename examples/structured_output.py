import asyncio
import os
import sys
import openai
import google.generativeai as genai
from agentflow import create_node

if "GEMINI_API_KEY" not in os.environ:
    print("ERROR: GEMINI_API_KEY environment variable is not set.")
    sys.exit(1)
if "OPENAI_API_KEY" not in os.environ:
    print("ERROR: OPENAI_API_KEY environment variable is not set.")
    sys.exit(1)

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

async def research(store):
    topic = store.get("topic", "")
    response = await openai.AsyncOpenAI().chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"List 5 key facts about {topic}."}],
        max_tokens=64,
        temperature=0.7,
    )
    store["research"] = response.choices[0].message.content
    return store

def summary_sync(store):
    research = store.get("research", "")
    model = genai.GenerativeModel("models/gemini-1.5-pro")
    response = model.generate_content(f"Summarize: {research}")
    store["summary"] = response.text
    return store

async def summary(store):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, summary_sync, store)

async def critique(store):
    summary = store.get("summary", "")
    response = await openai.AsyncOpenAI().chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Critique: {summary}"}],
        max_tokens=64,
        temperature=0.7,
    )
    store["critique"] = response.choices[0].message.content
    return store

async def structure(store):
    return {
        "status": "success",
        "topic": store.get("topic", ""),
        "research": store.get("research", ""),
        "summary": store.get("summary", ""),
        "critique": store.get("critique", ""),
    }

async def pipeline(store):
    store = await research(store)
    store = await summary(store)
    store = await critique(store)
    return await structure(store)

async def main():
    topic = "async Python"
    store = {"topic": topic}
    result = await pipeline(store)
    import json
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
