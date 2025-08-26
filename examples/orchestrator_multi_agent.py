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

async def research(store):
    topic = store.get("topic", "")
    response = await openai.AsyncOpenAI().chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"5 facts about {topic}"}],
        max_tokens=64,
        temperature=0.7,
    )
    store["research_facts"] = response.choices[0].message.content
    return store

def code_sync(store):
    facts = store.get("research_facts", "")
    model = genai.GenerativeModel("models/gemini-1.5-pro")
    response = model.generate_content(f"TypeScript code using: {facts}")
    store["typescript_code"] = response.text
    return store

async def code(store):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, code_sync, store)

async def review(store):
    code = store.get("typescript_code", "")
    response = await openai.AsyncOpenAI().chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Review this code: {code}"}],
        max_tokens=64,
        temperature=0.7,
    )
    store["review"] = response.choices[0].message.content
    return store

def pretty_print_results(results):
    print("\n" + "─" * 50)
    print("Results so far:")
    icons = {
        "research_facts": "◻️ Research",
        "typescript_code": "◼️ Code Generation",
        "review": "◾ Review"
    }
    for key, label in icons.items():
        if key in results:
            print(f"\n{label}\n{'-'*len(label)}\n{results[key]}")
    print("─" * 50 + "\n")

async def hitl_orchestrator(store):
    steps = [
        ("◻️ Research", research, "research_facts"),
        ("◼️ Code Generation", code, "typescript_code"),
        ("◾ Review", review, "review"),
    ]
    results = {}
    for step_name, step_func, result_key in steps:
        while True:
            store = await step_func(store)
            results[result_key] = store[result_key]
            print(f"\nStep: {step_name}")
            print(f"{result_key.replace('_', ' ').title()}:\n{store[result_key]}")
            print("\n[HITL] Enter your action: [a] Approve, [d] Deny, [c] Cancel, [r] Revise")
            user_input = input("Your choice: ").strip().lower()
            if user_input == "a":
                break  # Proceed to next step
            elif user_input == "d":
                print("\n[x] Approval denied. Displaying all previous results:")
                pretty_print_results(results)
                return store
            elif user_input == "c":
                print("\n[–] Process cancelled by user.")
                sys.exit(0)
            elif user_input == "r":
                print("\n[↻] Re-running the current step...")
                continue  # Re-run current step
            else:
                print("Invalid input. Please enter 'a', 'd', 'c', or 'r'.")
    # All steps approved
    print("\n[✓] All steps approved. Final results:")
    pretty_print_results(results)
    store["report"] = results
    return store

async def main():
    agent = Agent(create_node(hitl_orchestrator))
    store = {"topic": "maple syrup"}
    await agent.decide(store)

if __name__ == "__main__":
    asyncio.run(main())
