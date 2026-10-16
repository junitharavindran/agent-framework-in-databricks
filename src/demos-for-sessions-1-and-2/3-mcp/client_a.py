"""
MCP client A: talks to Server A over STDIO.

    python client_a.py

The client starts servers.py as a child process, so there is nothing else to run.

Commands:
    list            show the tools the server offers
    call <tool>     call a tool (you are asked for each argument)
    quit            exit
"""

import asyncio
import sys

from mcp import Client, StdioServerParameters


def text_of(result) -> str:
    return "".join(getattr(part, "text", "") for part in result.content)


async def ask(prompt: str) -> str:
    return (await asyncio.to_thread(input, prompt)).strip()


async def collect_args(schema: dict) -> dict:
    """Ask the user for each argument listed in a tool's input schema."""
    args = {}
    for name, spec in schema.get("properties", {}).items():
        value = await ask(f"  {name} ({spec.get('type', 'string')}): ")
        if spec.get("type") == "integer":
            value = int(value)
        elif spec.get("type") == "number":
            value = float(value)
        args[name] = value
    return args


async def main() -> None:
    params = StdioServerParameters(command=sys.executable, args=["servers.py", "a"])
    async with Client(params) as client:
        print(f"Connected to: {client.server_info.name}  (STDIO)")
        print("Commands: list | call <tool> | quit")

        while True:
            line = await ask("\n> ")
            cmd, _, arg = line.partition(" ")
            arg = arg.strip()

            try:
                if cmd in ("quit", "exit", "q"):
                    break

                elif cmd == "list":
                    for t in (await client.list_tools()).tools:
                        print(f"  {t.name}: {t.description}")

                elif cmd == "call" and arg:
                    tools = {t.name: t for t in (await client.list_tools()).tools}
                    if arg not in tools:
                        print(f"  no such tool: {arg}  (try 'list')")
                        continue
                    args = await collect_args(tools[arg].input_schema)
                    print("  ->", text_of(await client.call_tool(arg, args)))

                else:
                    print("  Commands: list | call <tool> | quit")

            except Exception as e:  # keep the loop alive on bad input
                print(f"  error: {e}")


if __name__ == "__main__":
    asyncio.run(main())