import asyncio
import os
import sys
import openai
import google.generativeai as genai
from agentflow import Workflow, create_node

if "GEMINI_API_KEY" not in os.environ:
    print("ERROR: GEMINI_API_KEY environment variable is not set.")
    sys.exit(1)
if "OPENAI_API_KEY" not in os.environ:
    print("ERROR: OPENAI_API_KEY environment variable is not set.")
    sys.exit(1)

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

async def openai_step(store):
    prompt = "Research the impact of async programming."
    response = await openai.AsyncOpenAI().chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=64,
        temperature=0.7,
    )
    store["step1"] = response.choices[0].message.content
    store["action"] = "default"
    return store

def gemini_step_sync(store):
    prompt = "Generate a code example for async in Python."
    model = genai.GenerativeModel("models/gemini-1.5-pro")
    response = model.generate_content(prompt)
    store["step2"] = response.text
    store["action"] = "default"
    return store

async def gemini_step(store):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, gemini_step_sync, store)

async def main():
    wf = Workflow()
    wf.add_step("step1", create_node(openai_step))
    wf.add_step("step2", create_node(gemini_step))
    wf.connect("step1", "step2")

    result = await wf.run({})
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
