# FusionCHMIngest Specification

## Project Overview

**Project Name:** FusionCHMIngest  
**Goal:** Convert Fusion360 API CHM documentation to Markdown and store in a vector database for AI coding agent retrieval  
**Platform:** macOS Tahoe  
**Installation:** Homebrew  

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    FusionCHMIngest Pipeline                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐   │
│  │  CHM File   │───▶│ CHM→Markdown │───▶│   Markdown       │   │
│  │ (resources) │    │  Converter   │    │   Output         │   │
│  └──────────────┘    └──────────────┘    └────────┬─────────┘   │
│                                                    │             │
│                                                    ▼             │
│                              ┌────────────────────────────────┐  │
│                              │   Chunking Strategy            │  │
│                              │   (by heading + overlap)      │  │
│                              └────────────┬─────────────────┘  │
│                                           │                    │
│                                           ▼                    │
│                              ┌────────────────────────────────┐  │
│                              │   Embedding (Local)            │  │
│                              │   sentence-transformers        │  │
│                              │   (all-MiniLM-L6-v2)          │  │
│                              └────────────┬─────────────────┘  │
│                                           │                    │
│                                           ▼                    │
│                              ┌────────────────────────────────┐  │
│                              │   Chroma Vector DB            │  │
│                              │   (local persistence)         │  │
│                              └────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. CHM to Markdown Converter (Existing)

**Location:** `chm_to_markdown.py` (modified for Fusion360)

**Modifications needed:**
- Add Fusion360-specific code snippet handling (JavaScript/Python API)
- Handle Fusion360 API class/method formatting
- Update output structure for Fusion360 versioning

### 2. Markdown Chunker

**New file:** `chunk_markdown.py`

**Strategy:**
- Split by heading levels (H1-H3)
- Preserve code blocks as atomic units
- Configurable overlap (10-20%)
- Default chunk size: 1000 tokens
- Metadata extraction: title, API class/method, member type

### 3. Embedding Engine

**New file:** `embed_documents.py`

**Configuration:**
- Model: `sentence-transformers/all-MiniLM-L6-v2` (runs on Apple Silicon)
- Fallback: `sentence-transformers/all-mpnet-base-v2`
- Device: `mps` (Apple Silicon GPU) with CPU fallback

### 4. Vector Store Manager

**New file:** `vector_store.py`

**Chroma configuration:**
- Persist directory: `~/.fusionchmingest/vectorstore/`
- Collection: `fusion360_api_docs`
- Metadata fields: `title`, `source_file`, `api_type`, `version`, `method_name`, `property_type`

### 5. MCP Server (Primary Access for AI Agents)

**New file:** `mcp_server.py`

**Server Type:** Using [FastMCP](https://github.com/jlowin/fastmcp) or [MCP SDK](https://modelcontextprotocol.io/)

#### Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `search_fusion_docs` | Semantic search of Fusion360 API documentation | `query: string`, `top_k: int (default: 5)` |
| `get_api_class` | Get full documentation for a specific API class | `class_name: string` |
| `get_api_example` | Get code example for a class or method | `class_name: string`, `method_name: string (optional)` |
| `list_api_classes` | List all available API classes | `filter: string (optional)` |

#### Resources

| URI | Description |
|-----|-------------|
| `fusion://docs/{class_name}` | Full documentation for an API class |
| `fusion://examples/{class_name}` | Code examples for a class |
| `fusion://index` | Complete API class index |

#### Prompts

| Prompt | Description |
|--------|-------------|
| `how_to_create_feature` | "Show me how to create a feature using the Fusion 360 API" |
| `api_example_for` | Generate an API example for a specific task |

**Start command:**
```bash
fusionchmingest mcp
# or
python -m fusionchmingest.mcp
```

#### MCP Integration Flow

```
┌─────────────────┐        MCP        ┌──────────────────────────┐
│   Claude        │◀─────────────────▶│   FusionCHMIngest       │
│   Agent /       │                    │   MCP Server             │
│   Cursor        │   search_fusion_docs│   (local)               │
│                 │   get_api_example  │                         │
│                 │   get_api_class    │   Tools → Vector Store   │
│                 │   list_api_classes │   Resources → Markdown   │
└─────────────────┘                    └──────────────────────────┘
```

### 6. CLI Interface (Optional)

**New file:** `cli.py` (using argparse or click)

**Commands:**
```bash
fusionchmingest convert      # Convert CHM to Markdown
fusionchmingest ingest      # Run full pipeline (convert + embed)
fusionchmingest search      # Query the vector DB (CLI fallback)
fusionchmingest update      # Check for and apply updates
fusionchmingest mcp         # Start MCP server (primary)
fusionchmingest serve       # Start REST API server (optional)
```

## Homebrew Integration

### Formula

**File:** `Formula/fusionchmingest.rb`

**Dependencies:**
- Python 3.11+ 
- 7zz (via Homebrew)

**Python packages:**
- beautifulsoup4
- html2text
- aiofiles
- chromadb
- sentence-transformers
- torch (MPS support)
- fastmcp (or mcp library)
- click (CLI)

## Directory Structure

```
FusionCHMIngest/
├── chm_to_markdown.py      # CHM → Markdown converter (modified)
├── chunk_markdown.py        # Markdown chunking
├── embed_documents.py       # Embedding generation
├── vector_store.py         # Chroma DB management
├── mcp_server.py           # MCP server (primary agent interface)
├── cli.py                   # CLI interface
├── requirements.txt         # Python dependencies
├── Formula/
│   └── fusionchmingest.rb  # Homebrew formula
├── resources/              # Input CHM files
│   └── FusionAPI.chm
├── output/                 # Generated Markdown
├── README.md
└── spec.md                 # This specification
```

## Documentation Standards

### README.md Formatting

All README.md sections using numbered steps must follow this pattern:

1. **Numbered list format**: Use "1." for each step (not sequential numbers)
2. **Description text**: Each step must have a descriptive sentence before the bash block
3. **No comments in bash blocks**: Never use "#" comments inside bash code fences
4. **Consistent structure**: Each step = description + bash code block

**Example:**

```markdown
1. Uninstall the app.
```bash
brew uninstall fusionchmingest
```
1. Remove user data (vector store).
```bash
rm -rf ~/.fusionchmingest
```
```

**Incorrect:**

```markdown
```bash
# Uninstall the app
brew uninstall fusionchmingest
```
```

## Update Mechanism

Since updates come every ~3 months:
1. Download new CHM from Autodesk URL
2. Place in `resources/` folder
3. Run `fusionchmingest update` or `brew upgrade fusionchmingest`
4. Tool re-runs full pipeline, preserving/regenerating embeddings

## Output Artifacts

- **Markdown:** `output/FusionAPI/{data,core}/` (existing structure)
- **Vector Store:** `~/.fusionchmingest/vectorstore/chroma.sqlite3`
- **Metadata:** `~/.fusionchmingest/vectorstore/metadata.json`

## Access for Coding Agents

### Primary: MCP Server

The MCP server is the primary interface for AI coding agents (Claude, Cursor, etc.):

1. **Start MCP server:**
   ```bash
   fusionchmingest mcp
   ```

2. **Agent configuration:** Add to agent's MCP config:
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

3. **Agent usage:** The agent can now call tools like:
   - `search_fusion_docs("create a sketch")` → Returns relevant docs with code examples
   - `get_api_class("Feature")` → Returns full Feature class documentation
   - `get_api_example("Component", "add")` → Returns add method code examples

### Optional: CLI / REST API

Fallback options for non-MCP agents:
- **CLI:** `fusionchmingest search "how to create a component"`
- **Python API:** Import and query programmatically
- **REST API:** `fusionchmingest serve --port 8080`

## Credits

- Original project: Forked from [chm-converter](https://github.com/DTDucas/chm-converter) by [DTDucas](https://github.com/DTDucas)
- Input: [Fusion360 API CHM Documentation](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/ExtraFiles/FusionAPI.chm)
