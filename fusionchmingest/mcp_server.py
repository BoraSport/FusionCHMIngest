import sys
from typing import Any

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

from fusionchmingest.vector_store import VectorStore, QueryResult

MCP_SERVER_NAME = "FusionCHMIngest"

def format_search_results(results: list[QueryResult]) -> str:
    if not results:
        return "No results found."
    output = []
    for i, result in enumerate(results, 1):
        chunk = result.chunk
        output.append(f"--- Result {i} (distance: {result.distance:.4f}) ---")
        output.append(f"**{chunk.title}**")
        output.append(f"Source: {chunk.source_file}")
        if chunk.method_name:
            output.append(f"Method: {chunk.method_name}")
        output.append("")
        content = chunk.content[:500] + "..." if len(chunk.content) > 500 else chunk.content
        output.append(content)
        output.append("")
    return "\n".join(output)

def format_class_docs(chunks: list) -> str:
    if not chunks:
        return "No documentation found for this class."
    output = []
    for chunk in chunks:
        output.append(f"## {chunk.title}")
        output.append(f"Source: {chunk.source_file}")
        output.append("")
        output.append(chunk.content)
        output.append("")
    return "\n".join(output)

def format_examples(chunks: list) -> str:
    if not chunks:
        return "No code examples found."
    output = ["## Code Examples", ""]
    for chunk in chunks:
        output.append(f"### {chunk.title}")
        if chunk.method_name:
            output.append(f"Method: `{chunk.method_name}`")
        output.append("")
        output.append(chunk.content)
        output.append("")
    return "\n".join(output)

async def serve() -> None:
    if not MCP_AVAILABLE:
        print("Error: MCP library not installed. Install with: pip install mcp")
        sys.exit(1)
    
    server = Server(MCP_SERVER_NAME)
    
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(name="search_fusion_docs", description="Search Fusion360 API documentation using semantic search",
                 inputSchema={"type": "object", "properties": {"query": {"type": "string", "description": "Search query"},
                 "top_k": {"type": "integer", "description": "Number of results", "default": 5}}, "required": ["query"]}),
            Tool(name="get_api_class", description="Get full documentation for a specific Fusion360 API class",
                 inputSchema={"type": "object", "properties": {"class_name": {"type": "string"}}, "required": ["class_name"]}),
            Tool(name="get_api_example", description="Get code examples for a Fusion360 API class or method",
                 inputSchema={"type": "object", "properties": {"class_name": {"type": "string"},
                 "method_name": {"type": "string"}}, "required": ["class_name"]}),
            Tool(name="list_api_classes", description="List all available Fusion360 API classes",
                 inputSchema={"type": "object", "properties": {"filter": {"type": "string"}}}),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Any) -> list[TextContent]:
        vs = VectorStore()
        if name == "search_fusion_docs":
            results = vs.query(arguments.get("query", ""), arguments.get("top_k", 5))
            return [TextContent(type="text", text=format_search_results(results))]
        elif name == "get_api_class":
            chunks = vs.get_by_class(arguments.get("class_name", ""))
            return [TextContent(type="text", text=format_class_docs(chunks))]
        elif name == "get_api_example":
            chunks = vs.get_examples(arguments.get("class_name", ""), arguments.get("method_name"))
            return [TextContent(type="text", text=format_examples(chunks))]
        elif name == "list_api_classes":
            classes = vs.list_classes(arguments.get("filter"))
            output = f"## Available API Classes ({len(classes)} total)\n\n" + "\n".join(f"- {cls}" for cls in classes) if classes else "No classes found."
            return [TextContent(type="text", text=output)]
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

def main():
    import asyncio
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        print("\nMCP server stopped.")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting MCP server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
