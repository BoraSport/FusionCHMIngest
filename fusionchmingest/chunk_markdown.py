import os, re, uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    import tiktoken
    TOKENIZER_AVAILABLE = True
except ImportError:
    TOKENIZER_AVAILABLE = False

from fusionchmingest.vector_store import Chunk

DEFAULT_CHUNK_SIZE = 1000
DEFAULT_OVERLAP = 100

def count_tokens(text: str, encoding_name: str = "cl100k_base") -> int:
    if not TOKENIZER_AVAILABLE:
        return len(text.split())
    encoder = tiktoken.get_encoding(encoding_name)
    return len(encoder.encode(text))

def extract_heading_level(line: str) -> Optional[int]:
    match = re.match(r'^(#{1,6})\s+(.+)$', line)
    return len(match.group(1)) if match else None

def extract_title_from_content(content: str) -> str:
    for line in content.strip().split('\n'):
        level = extract_heading_level(line)
        if level and level <= 2:
            return line.lstrip('#').strip()
    return ""

def extract_api_info(title: str) -> tuple[Optional[str], Optional[str]]:
    class_match = re.match(r'^(\w+)(?:\.(.+))?$', title)
    if class_match:
        class_name = class_match.group(1)
        member = class_match.group(2)
        return class_name, member
    return None, None

def split_by_headings(content: str, chunk_size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_OVERLAP) -> list[str]:
    lines = content.split('\n')
    chunks = []
    current_chunk = []
    for line in lines:
        if extract_heading_level(line):
            if current_chunk:
                chunks.append('\n'.join(current_chunk))
            current_chunk = []
        current_chunk.append(line)
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    return chunks

def chunk_markdown_file(file_path: str, chunk_size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_OVERLAP, version: str = "unknown") -> list[Chunk]:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    source_file = os.path.basename(file_path)
    title = extract_title_from_content(content)
    api_class, method_name = extract_api_info(title)
    heading_chunks = split_by_headings(content, chunk_size, overlap)
    chunks = []
    for i, chunk_text in enumerate(heading_chunks):
        chunk_id = f"{source_file}_{i}_{uuid.uuid4().hex[:8]}"
        chunk_title = extract_title_from_content(chunk_text) or title
        chunk_api_class, chunk_method = extract_api_info(chunk_title)
        api_type = "class"
        if "example" in chunk_text.lower() or "code" in chunk_text.lower():
            api_type = "example"
        elif chunk_method:
            api_type = "method"
        chunks.append(Chunk(
            chunk_id=chunk_id, content=chunk_text, title=chunk_title, source_file=source_file,
            api_type=api_type, method_name=chunk_method or chunk_api_class, heading_level=1, version=version,
        ))
    return chunks

def process_all_markdown_files(input_dir: str, version: str = "unknown") -> list[Chunk]:
    input_path = Path(input_dir)
    if not input_path.exists():
        raise ValueError(f"Input directory does not exist: {input_dir}")
    md_files = list(input_path.rglob("*.md"))
    all_chunks = []
    for md_file in md_files:
        try:
            chunks = chunk_markdown_file(str(md_file), version=version)
            all_chunks.extend(chunks)
            print(f"Processed {md_file.name}: {len(chunks)} chunks")
        except Exception as e:
            print(f"Error processing {md_file}: {e}")
    return all_chunks
