import asyncio
import httpx
from agentflowpy import Agent, create_node

CMD_TOOL_URL = "http://localhost:3001/mcp"

async def cmd_tool_node(store):
    payload = {
        "name": "execute_command",
        "arguments": {
            "command": store.get("command", "echo"),
            "args": store.get("args", ["Hello! from Model-Context-Protocol (MCP) tool AI Agent"])
        }
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(CMD_TOOL_URL, json=payload)
        resp.raise_for_status()
        result = resp.json()
    store["cmd_result"] = result["content"][0]["text"] if result.get("success") else result
    return store

async def main():
    agent = Agent(create_node(cmd_tool_node), max_retries=3, wait_millis=500)
    store = {"command": "echo", "args": ["Agent with retry!"]}
    result = await agent.decide(store)
    print("Result:", result["cmd_result"])

if __name__ == "__main__":
    asyncio.run(main())
