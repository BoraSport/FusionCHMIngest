# FusionCHMIngest

Convert Fusion360 API documentation to vector embeddings for AI coding agents.

## Features

- Convert Fusion360 API CHM documentation to Markdown
- Generate vector embeddings using sentence-transformers
- Store in ChromaDB vector database for semantic search
- MCP server for AI agent integration (Claude, Cursor, etc.)
- Apple Silicon (MPS) GPU support for embedding generation

## Installation

### Homebrew (macOS)

```bash
brew install fusionchmingest
```

### From Source

```bash
# Clone the repository
git clone https://github.com/BoraSport/FusionCHMIngest.git
cd FusionCHMIngest

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .
```

## Usage

### CLI Commands

```bash
# Convert CHM to Markdown
fusionchmingest convert

# Run full pipeline (convert + embed + store)
fusionchmingest ingest

# Search the vector database
fusionchmingest search "how to create a component"

# Get documentation for a specific class
fusionchmingest get-class Feature

# List all available API classes
fusionchmingest list-classes

# Start MCP server for AI agents
fusionchmingest mcp

# Check status
fusionchmingest status
```

### MCP Server

The MCP server provides tools for AI coding agents:

| Tool | Description |
|------|-------------|
| `search_fusion_docs` | Semantic search of Fusion360 API docs |
| `get_api_class` | Get full documentation for a class |
| `get_api_example` | Get code examples |
| `list_api_classes` | List all available classes |

## Requirements

- Python 3.11+
- chromadb
- sentence-transformers
- torch
- click

## Derived From

This project is derived from [chm-converter](https://github.com/DTDucas/chm-converter) by Duong Tran Quang (DTDucas).

Original author: baymax.contact@gmail.com

## License

MIT
