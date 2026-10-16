"""
Block 1.5 (demo): A host with 2 MCP clients, one per server.

    python client.py

It starts Server A itself (STDIO, as a child process) and Server B (Streamable HTTP, as a separate process), connects one client to each, and prints what each connection sees. Note that each client talks to exactly one server.
"""

import asyncio
import socket
import subprocess
import sys
import time

from mcp import Client, StdioServerParameters

URL_B = "http://127.0.0.1:8765/mcp"
SERVERS = "servers.py"


def wait_for_port(port: int, timeout: float = 15) -> None:
    end = time.time() + timeout
    while time.time() < end:
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", port)) == 0:
                return
        time.sleep(0.2)
    raise RuntimeError(f"server on port {port} did not start")


def text_of(result) -> str:
    return "".join(getattr(part, "text", "") for part in result.content)


async def main() -> None:
    http_server = subprocess.Popen([sys.executable, SERVERS, "b"], stderr=subprocess.DEVNULL)
    try:
        wait_for_port(8765)

        params_a = StdioServerParameters(command=sys.executable, args=[SERVERS, "a"])
        async with Client(params_a) as client_a, Client(URL_B) as client_b:
            # --- the pairing: client A <-> server A, client B <-> server B ---
            print(f"client A is connected to: {client_a.server_info.name}  (STDIO)")
            print(f"client B is connected to: {client_b.server_info.name}  (Streamable HTTP)")

            # --- primitive 1: tools (the model decides to call them) ---
            print("\nTOOLS on A:", [t.name for t in (await client_a.list_tools()).tools])
            print("TOOLS on B:", [t.name for t in (await client_b.list_tools()).tools])
            r = await client_a.call_tool("check_spelling", {"text": "an orignal reciept"})
            print("A.check_spelling ->", text_of(r))
            r = await client_b.call_tool("search_documents", {"query": "refund"})
            print("B.search_documents('refund') ->", text_of(r))

            # --- primitive 2: resources (data fetched by URI) ---
            doc = await client_b.read_resource("doc://1")
            print("\nRESOURCE doc://1 ->", doc.contents[0].text)

            # --- primitive 3: prompts (reusable templates) ---
            prompt = await client_b.get_prompt("analyse_paragraph", {"paragraph": "Gift purchases get credit insted of cash."})
            print("\nPROMPT ->", prompt.messages[0].content.text)
    finally:
        http_server.terminate()


if __name__ == "__main__":
    asyncio.run(main())
