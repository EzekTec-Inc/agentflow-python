import asyncio
import os
import sys
import openai
import google.generativeai as genai
from agentflow import MapReduce, create_node

if "GEMINI_API_KEY" not in os.environ:
    print("ERROR: GEMINI_API_KEY environment variable is not set.")
    sys.exit(1)
if "OPENAI_API_KEY" not in os.environ:
    print("ERROR: OPENAI_API_KEY environment variable is not set.")
    sys.exit(1)

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

async def mapper(store):
    doc = store.get("doc", "")
    response = await openai.AsyncOpenAI().chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Summarize: {doc}"}],
        max_tokens=64,
        temperature=0.7,
    )
    store["summary"] = response.choices[0].message.content
    return store

def reducer_sync(stores):
    all_summaries = [s.get("summary", "") for s in stores]
    model = genai.GenerativeModel("models/gemini-1.5-pro")
    response = model.generate_content("Aggregate these summaries:\n" + "\n".join(all_summaries))
    return {"all_summaries": response.text}

async def reducer(stores):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, reducer_sync, stores)

async def main():
    docs = [
        "Rust is a systems programming language.",
        "Async programming enables concurrency.",
        "LLMs are transforming software development.",
    ]
    stores = [{"doc": doc} for doc in docs]
    mapreduce = MapReduce(create_node(mapper), create_node(reducer))
    result = await mapreduce.call(stores)
    print("All Summaries:\n", result["all_summaries"])

if __name__ == "__main__":
    asyncio.run(main())
