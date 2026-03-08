# FusionCHMIngest

Convert Fusion360 API documentation to vector embeddings for AI coding agents.

## Features

- Convert Fusion360 API CHM documentation to Markdown
- Generate vector embeddings using sentence-transformers
- Store in ChromaDB vector database for semantic search
- MCP server for AI agent integration (Claude, Cursor, etc.)
- Apple Silicon (MPS) GPU support for embedding generation

## Installation

### Homebrew (macOS) - Recommended

> **Note:** This formula has not been submitted to Homebrew core yet. Installation requires adding a local tap.

#### Quick Install (if tap already exists)

```bash
brew install fusionchmingest
```

#### First-Time Setup: Create Local Tap

Since this formula isn't in Homebrew core yet, you need to set up a local tap once:

```bash
mkdir -p /opt/homebrew/Library/Taps/fusionchmingest
```

```bash
cp Formula/fusionchmingest.rb /opt/homebrew/Library/Taps/fusionchmingest/
```

```bash
brew install fusionchmingest
```

After the first install, you can update with:

```bash
brew update
```

```bash
brew upgrade fusionchmingest
```

#### Uninstall

```bash
# Uninstall the app
brew uninstall fusionchmingest
```

```bash
# Remove user data (vector store)
rm -rf ~/.fusionchmingest
```

```bash
# Or use zap to remove both app and user data
brew zap fusionchmingest
```

```bash
# Remove the local tap
rm -rf /opt/homebrew/Library/Taps/fusionchmingest
```

### From Source

```bash
# Clone the repository
git clone https://github.com/BoraSport/FusionCHMIngest.git
cd FusionCHMIngest

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .

# Verify installation
fusionchmingest --version
```

## Development Setup

### Prerequisites

- Python 3.11+
- Homebrew (for macOS)

### Setup

```bash
# Clone the repository
git clone https://github.com/BoraSport/FusionCHMIngest.git
cd FusionCHMIngest

# Remove and recreate virtual environment (if needed)
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# Install all dependencies
pip install -e .

# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

### Common Issues

**Broken venv**: If the venv doesn't work, delete and recreate:
```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

## Usage

### CLI Commands

```bash
# Show all available commands and options
fusionchmingest --help

# Convert CHM to Markdown (all files)
fusionchmingest convert --verbose

# Convert a specific CHM file
fusionchmingest convert --single 20260304-FusionAPI.chm

# Run full pipeline (convert + embed + store) - processes all CHM files
fusionchmingest ingest --verbose

# Run full pipeline for a specific CHM file
fusionchmingest ingest --single 20260304-FusionAPI.chm

# Run full pipeline for all CHM files in resources folder
fusionchmingest ingest --all

# Verify CHM was processed successfully
fusionchmingest verify

# Search the vector database
fusionchmingest search "how to create a component"

# Get documentation for a specific class
fusionchmingest get-class Feature

# List all available API classes
fusionchmingest list-classes

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

### Connecting AI Agents

#### Claude Desktop

1. Open `~/Library/Application Support/Claude/claude_desktop_config.json`
2. Add this configuration:

```json
{
  "mcpServers": {
    "fusion360-api": {
      "command": "fusionchmingest",
      "args": ["mcp"]
    }
  }
}
```

3. Restart Claude Desktop

#### Cursor

1. Open Cursor settings
2. Navigate to MCP configuration
3. Add this configuration:

```json
{
  "mcpServers": {
    "fusion360-api": {
      "command": "fusionchmingest",
      "args": ["mcp"]
    }
  }
}
```

4. Restart Cursor

#### VS Code + GitHub Copilot

1. Open VS Code settings (JSON): `Cmd+,` then click the Open Settings (JSON) icon
2. Add this configuration:

```json
{
  "github.copilot.advanced.mcpServers": {
    "fusion360-api": {
      "command": "fusionchmingest",
      "args": ["mcp"]
    }
  }
}
```

3. Restart VS Code

#### OpenCode

Add the same configuration to OpenCode's MCP settings:

```json
{
  "mcpServers": {
    "fusion360-api": {
      "command": "fusionchmingest",
      "args": ["mcp"]
    }
  }
}
```

#### Auto-Configure

Run this command to generate the configuration:

```bash
fusionchmingest mcp-config
```

This will output the JSON configuration for your agent.

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
