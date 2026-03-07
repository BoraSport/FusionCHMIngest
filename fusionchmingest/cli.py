import asyncio
import os
import click
from pathlib import Path

from fusionchmingest.vector_store import VectorStore


__version__ = "1.0.0"


@click.group()
@click.version_option(version=__version__)
def cli():
    """FusionCHMIngest - Fusion360 API Documentation for AI Agents"""
    pass


@cli.command()
@click.option("--verbose", "-v", is_flag=True, help="Show detailed progress")
def convert(verbose):
    """Convert CHM to Markdown"""
    if verbose:
        click.echo("Starting CHM to Markdown conversion (verbose mode)...")
    else:
        click.echo("Converting CHM to Markdown...")
    from fusionchmingest.chm_to_markdown import main as convert_main
    asyncio.run(convert_main(verbose=verbose))


@cli.command()
@click.option("--verbose", "-v", is_flag=True, help="Show detailed progress")
@click.option("--single", "-s", help="Process a single CHM file")
@click.option("--all", "-a", "process_all", is_flag=True, help="Process all CHM files in resources folder")
def ingest(verbose, single, process_all):
    """Run full pipeline (convert + embed)"""
    if verbose:
        click.echo("Starting full pipeline (verbose mode)...")
    else:
        click.echo("Running full pipeline...")
    
    from fusionchmingest.chm_to_markdown import main as convert_main
    from fusionchmingest.chunk_markdown import process_all_markdown_files
    from fusionchmingest.embed_documents import embed_chunks
    
    if verbose:
        click.echo("\n=== Step 1: Converting CHM to Markdown ===")
    else:
        click.echo("Step 1: Converting CHM to Markdown...")
    asyncio.run(convert_main(verbose=verbose, single=single, process_all=process_all))
    
    output_dir = "output"
    if not os.path.exists(output_dir):
        click.echo("No output directory found. Conversion may have failed.")
        return
    
    version = "latest"
    
    chunks = []
    total_chunks = 0
    for root, dirs, files in os.walk(output_dir):
        for d in dirs:
            if d == "data":
                data_dir = os.path.join(root, d)
                chunks = process_all_markdown_files(data_dir, version=version)
                total_chunks = len(chunks)
                if verbose:
                    click.echo(f"Created {len(chunks)} chunks from {data_dir}")
                else:
                    click.echo(f"Created {len(chunks)} chunks")
                break
    
    if total_chunks == 0:
        click.echo("No chunks created. Check that markdown files exist.")
        return
    
    if verbose:
        click.echo("\n=== Step 3: Generating embeddings ===")
    else:
        click.echo("Step 3: Generating embeddings...")
    
    try:
        from fusionchmingest.embed_documents import ChunkWithEmbedding
        chunks_with_embeddings = embed_chunks(chunks)
        if verbose:
            click.echo(f"Generated {len(chunks_with_embeddings)} embeddings")
        chunks_to_store = [cwe.chunk for cwe in chunks_with_embeddings]
    except Exception as e:
        if verbose:
            click.echo(f"Warning: Could not generate embeddings: {e}")
        chunks_to_store = chunks
    
    if verbose:
        click.echo("\n=== Step 4: Storing in vector database ===")
    else:
        click.echo("Step 4: Storing in vector database...")
    
    try:
        vs = VectorStore()
        vs.add_chunks(chunks_to_store)
        if verbose:
            click.echo(f"Added {len(chunks_to_store)} chunks to vector store")
        else:
            click.echo(f"Added {len(chunks_to_store)} chunks to vector store")
    except Exception as e:
        if verbose:
            click.echo(f"Warning: Could not store in vector DB: {e}")
        click.echo("Pipeline complete! (vector storage skipped)")
        return
    
    click.echo("Pipeline complete!")
    
    chunk_count = vs.get_count()
    vector_store_path = os.path.expanduser("~/.fusionchmingest/vectorstore")
    
    click.echo("")
    click.echo("=" * 50)
    click.echo("Now connect to AI agents via MCP!")
    click.echo("=" * 50)
    click.echo("")
    click.echo(f"Vector store: {chunk_count} chunks")
    click.echo(f"Location: {vector_store_path}")
    click.echo("")
    click.echo("Add this to your AI agent's MCP settings:")
    click.echo("")
    click.echo("  {")
    click.echo("    \"mcpServers\": {")
    click.echo("      \"fusion360-api\": {")
    click.echo("        \"command\": \"fusionchmingest\",")
    click.echo("        \"args\": [\"mcp\"]")
    click.echo("      }")
    click.echo("    }")
    click.echo("  }")
    click.echo("")
    click.echo("For more options, run: fusionchmingest mcp-config")


@cli.command()
def verify():
    """Verify that CHM was processed successfully"""
    click.echo("=== FusionCHMIngest Verification ===\n")
    
    issues_found = 0
    
    # Check output directory
    output_dir = "output"
    if not os.path.exists(output_dir):
        click.echo("❌ Output directory not found")
        click.echo("   Run 'fusionchmingest convert' first")
        issues_found += 1
    else:
        # Count markdown files
        md_files = list(Path(output_dir).rglob("*.md"))
        click.echo(f"✓ Output directory exists")
        click.echo(f"  Found {len(md_files)} markdown files")
        
        if len(md_files) == 0:
            click.echo("  ⚠ No markdown files found in output directory")
            issues_found += 1
    
    # Check data directory
    data_dir = os.path.join(output_dir, "FusionAPI", "data")
    if os.path.exists(data_dir):
        data_files = list(Path(data_dir).rglob("*.md"))
        click.echo(f"  Data directory: {len(data_files)} files")
    else:
        click.echo("  ⚠ Data directory not found")
    
    # Check vector store
    click.echo("")
    try:
        vs = VectorStore()
        count = vs.get_count()
        if count > 0:
            click.echo(f"✓ Vector store initialized")
            click.echo(f"  Contains {count} chunks")
        else:
            click.echo("⚠ Vector store is empty")
            click.echo("  Run 'fusionchmingest ingest' to add embeddings")
            issues_found += 1
    except Exception as e:
        click.echo(f"❌ Vector store error: {e}")
        issues_found += 1
    
    # Summary
    click.echo("")
    if issues_found == 0:
        click.echo("✅ Verification passed! CHM was processed successfully.")
    else:
        click.echo(f"⚠ Verification found {issues_found} issue(s).")
        click.echo("   Run 'fusionchmingest ingest' to complete processing.")


@cli.command()
@click.argument("query")
@click.option("--top-k", default=5, help="Number of results to return")
def search(query, top_k):
    """Query the vector database"""
    click.echo(f"Searching for: {query}")
    try:
        vs = VectorStore()
        results = vs.query(query, top_k)
        if not results:
            click.echo("No results found.")
            return
        click.echo(f"\nFound {len(results)} results:\n")
        for i, result in enumerate(results, 1):
            chunk = result.chunk
            click.echo(f"--- Result {i} (distance: {result.distance:.4f}) ---")
            click.echo(f"**{chunk.title}**")
            click.echo(f"Source: {chunk.source_file}")
            if chunk.method_name:
                click.echo(f"Method: {chunk.method_name}")
            click.echo("")
            content = chunk.content[:300] + "..." if len(chunk.content) > 300 else chunk.content
            click.echo(content)
            click.echo("")
    except Exception as e:
        click.echo(f"Error: {e}")


@cli.command()
@click.argument("class_name")
def get_class(class_name):
    """Get documentation for a specific API class"""
    try:
        vs = VectorStore()
        chunks = vs.get_by_class(class_name)
        if not chunks:
            click.echo(f"No documentation found for class: {class_name}")
            return
        for chunk in chunks:
            click.echo(f"## {chunk.title}")
            click.echo(f"Source: {chunk.source_file}")
            click.echo("")
            click.echo(chunk.content)
            click.echo("")
    except Exception as e:
        click.echo(f"Error: {e}")


@cli.command()
@click.argument("class_name")
@click.option("--method", help="Specific method name")
def examples(class_name, method):
    """Get code examples for an API class"""
    try:
        vs = VectorStore()
        chunks = vs.get_examples(class_name, method)
        if not chunks:
            click.echo(f"No examples found for: {class_name}")
            return
        for chunk in chunks:
            click.echo(f"### {chunk.title}")
            if chunk.method_name:
                click.echo(f"Method: `{chunk.method_name}`")
            click.echo("")
            click.echo(chunk.content)
            click.echo("")
    except Exception as e:
        click.echo(f"Error: {e}")


@cli.command()
def list_classes():
    """List all available API classes"""
    try:
        vs = VectorStore()
        classes = vs.list_classes()
        if not classes:
            click.echo("No classes found. Run 'ingest' first.")
            return
        click.echo(f"Available API Classes ({len(classes)} total):\n")
        for cls in classes:
            click.echo(f"  - {cls}")
    except Exception as e:
        click.echo(f"Error: {e}")


@cli.command()
def update():
    """Check for and apply documentation updates"""
    click.echo("Checking for updates...")
    click.echo("This feature is coming soon.")


@cli.command()
def mcp():
    """Start MCP server for AI agent integration"""
    click.echo("Starting MCP server...")
    from fusionchmingest.mcp_server import main as mcp_main
    mcp_main()


@cli.command()
def mcp_config():
    """Show MCP configuration for AI agents"""
    config = {
        "mcpServers": {
            "fusion360-api": {
                "command": "fusionchmingest",
                "args": ["mcp"]
            }
        }
    }
    import json
    click.echo("=== MCP Configuration ===\n")
    click.echo("Add this to your agent's MCP configuration:\n")
    click.echo(json.dumps(config, indent=2))
    click.echo("\n=== Claude Desktop ===")
    click.echo("File: ~/Library/Application Support/Claude/claude_desktop_config.json")
    click.echo("\n=== Cursor ===")
    click.echo("Settings > MCP > Add new server")
    click.echo("\n=== VS Code + GitHub Copilot ===")
    click.echo("Settings > Extensions > GitHub Copilot > Advanced > MCP Servers")
    click.echo("Or add to settings.json:")
    vscode_config = {
        "github.copilot.advanced.mcpServers": {
            "fusion360-api": {
                "command": "fusionchmingest",
                "args": ["mcp"]
            }
        }
    }
    click.echo(json.dumps(vscode_config, indent=2))
    click.echo("\n=== OpenCode ===")
    click.echo("Add via Settings > MCP configuration")


@cli.command()
def serve():
    """Start REST API server (optional)"""
    click.echo("Starting REST API server...")
    click.echo("This feature is coming soon.")


@cli.command()
def status():
    """Show vector store status"""
    try:
        vs = VectorStore()
        count = vs.get_count()
        click.echo(f"Vector store contains {count} chunks")
    except Exception as e:
        click.echo(f"Error: {e}")


if __name__ == "__main__":
    cli()
