"""Block 1.5 (demo): two small MCP servers.

Server A (STDIO):            word_count and spell_check tools
Server B (Streamable HTTP):  a search_documents tool, a doc://<id> resource,
                             and an "analyse this paragraph" prompt

Run one server by hand:
    python servers.py a            # STDIO: normally started BY the client
    python servers.py b            # HTTP on http://127.0.0.1:8765/mcp
"""
import re
import sys

from mcp.server.mcpserver import MCPServer


KNOWN_MISSPELLINGS = {"orignal": "original", "insted": "instead", "recieve": "receive"}


def word_count(text: str) -> int:
    return len(text.split())


def spell_check(text: str) -> str:
    words = re.findall(r"[a-zA-Z']+", text.lower())
    hits = [f"{w} -> {KNOWN_MISSPELLINGS[w]}" for w in words if w in KNOWN_MISSPELLINGS]
    return "misspelled: " + ", ".join(hits) if hits else "no misspellings"


DOCS = {
    "1": "Refunds are issued within five business days.",
    "2": "Gift purchases get store credit instead of cash.",
    "3": "Items can be returned within thirty days of purchase.",
}

#================================================
# Server A: tools only, over STDIO

server_a = MCPServer("proofreading-tools")


@server_a.tool()
def count_words(text: str) -> int:
    """Count the words in a text."""
    return word_count(text)


@server_a.tool()
def check_spelling(text: str) -> str:
    """List misspelled words in a text, with corrections."""
    return spell_check(text)

#================================================
# Server B: a tool, a resource and a prompt, over Streamable HTTP

server_b = MCPServer("policy-documents")


@server_b.tool()
def search_documents(query: str) -> list[str]:
    """Return the ids of documents containing the query (the model decides to call this)."""
    return [i for i, text in DOCS.items() if query.lower() in text.lower()]


@server_b.resource("doc://{doc_id}")
def read_document(doc_id: str) -> str:
    """A read-only document, fetched by URI (the application decides to read this)."""
    return DOCS[doc_id]


@server_b.prompt()
def analyse_paragraph(paragraph: str) -> str:
    """A reusable template (the user picks this)."""
    return f"Proofread this paragraph and list any spelling problems:\n\n{paragraph}"

#================================================
if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "a"
    if which == "a":
        server_a.run(transport="stdio")
    else:
        server_b.run(transport="streamable-http", host="127.0.0.1", port=8765)
