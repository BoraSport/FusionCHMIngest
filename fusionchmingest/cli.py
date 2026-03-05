import asyncio
import click
from fusionchmingest.vector_store import VectorStore


__version__ = "0.1.0"


@click.group()
@click.version_option(version=__version__)
def cli():
    """FusionCHMIngest - Fusion360 API Documentation for AI Agents"""
    pass


@cli.command()
def convert():
    """Convert CHM to Markdown"""
    click.echo("Converting CHM to Markdown...")
    from fusionchmingest.chm_to_markdown import main as convert_main
    asyncio.run(convert_main())


@cli.command()
def ingest():
    """Run full pipeline (convert + embed)"""
    click.echo("Running full pipeline...")
    from fusionchmingest.chm_to_markdown import main as convert_main
    from fusionchmingest.chunk_markdown import process_all_markdown_files
    from fusionchmingest.embed_documents import embed_chunks
    from fusionchmingest.vector_store import VectorStore
    import os
    
    click.echo("Step 1: Converting CHM to Markdown...")
    asyncio.run(convert_main())
    
    output_dir = "output"
    if not os.path.exists(output_dir):
        click.echo("No output directory found. Conversion may have failed.")
        return
    
    version = "latest"
    
    click.echo("Step 2: Chunking markdown files...")
    for root, dirs, files in os.walk(output_dir):
        for d in dirs:
            if d == "data":
                data_dir = os.path.join(root, d)
                chunks = process_all_markdown_files(data_dir, version=version)
                click.echo(f"Created {len(chunks)} chunks")
                
                click.echo("Step 3: Generating embeddings...")
                chunks_with_embeddings = embed_chunks(chunks)
                
                click.echo("Step 4: Storing in vector database...")
                vs = VectorStore()
                vs.add_chunks(chunks)
                click.echo(f"Added {len(chunks)} chunks to vector store")
                break
    
    click.echo("Pipeline complete!")


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
