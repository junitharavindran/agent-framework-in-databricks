"""
MCP client B: talks to Server B over Streamable HTTP.

First, in another terminal, start the server:
    python servers.py b

Then:
    python client_b.py

Commands:
    list                 show tools, resources and prompts
    call <tool>          call a tool (you are asked for each argument)
    read <uri>           read a resource, e.g. read doc://1
    prompt <name>        fetch a prompt template (you are asked for each argument)
    quit                 exit
"""

import asyncio

from mcp import Client

URL_B = "http://127.0.0.1:8765/mcp"


def text_of(result) -> str:
    """Return a comma-separated string combining all the parts of a result's content."""
    return ",".join(getattr(part, "text", "") for part in result.content)


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
    async with Client(URL_B) as client:
        print(f"Connected to: {client.server_info.name}  (Streamable HTTP)")
        print("Commands: list | call <tool> | read <uri> | prompt <name> | quit")

        while True:
            line = await ask("\n> ")
            cmd, _, arg = line.partition(" ")
            arg = arg.strip()

            try:
                if cmd in ("quit", "exit", "q"):
                    break

                elif cmd == "list":
                    print("TOOLS")
                    for t in (await client.list_tools()).tools:
                        print(f"  {t.name}: {t.description}")
                    print("RESOURCES")
                    for r in (await client.list_resources()).resources:
                        print(f"  {r.uri}")
                    for r in (await client.list_resource_templates()).resource_templates:
                        print(f"  {r.uri_template}  (template)")
                    print("PROMPTS")
                    for p in (await client.list_prompts()).prompts:
                        print(f"  {p.name}: {p.description}")

                elif cmd == "call" and arg:
                    tools = {t.name: t for t in (await client.list_tools()).tools}
                    if arg not in tools:
                        print(f"  no such tool: {arg}  (try 'list')")
                        continue
                    args = await collect_args(tools[arg].input_schema)
                    print("  ->", text_of(await client.call_tool(arg, args)))

                elif cmd == "read" and arg:
                    doc = await client.read_resource(arg)
                    print("  ->", doc.contents[0].text)

                elif cmd == "prompt" and arg:
                    prompts = {p.name: p for p in (await client.list_prompts()).prompts}
                    if arg not in prompts:
                        print(f"  no such prompt: {arg}  (try 'list')")
                        continue
                    args = {}
                    for a in prompts[arg].arguments or []:
                        args[a.name] = await ask(f"  {a.name}: ")
                    result = await client.get_prompt(arg, args)
                    print("  ->", result.messages[0].content.text)

                else:
                    print("  Commands: list | call <tool> | read <uri> | prompt <name> | quit")

            except Exception as e:  # keep the loop alive on bad input
                print(f"  error: {e}")


if __name__ == "__main__":
    asyncio.run(main())