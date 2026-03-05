import os
from dataclasses import dataclass
from typing import Optional

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    chromadb = None
    Settings = None


PERSIST_DIRECTORY = os.path.expanduser("~/.fusionchmingest/vectorstore")
COLLECTION_NAME = "fusion360_api_docs"


@dataclass
class Chunk:
    chunk_id: str
    content: str
    title: str
    source_file: str
    api_type: str
    method_name: Optional[str] = None
    property_type: Optional[str] = None
    heading_level: int = 1
    version: Optional[str] = None


@dataclass
class QueryResult:
    chunk: Chunk
    distance: float


class VectorStore:
    def __init__(self, persist_directory: Optional[str] = None, collection_name: str = COLLECTION_NAME):
        if not CHROMADB_AVAILABLE:
            raise ImportError("chromadb is required. Install with: pip install chromadb")
        
        self.persist_directory = persist_directory or PERSIST_DIRECTORY
        self.collection_name = collection_name
        os.makedirs(self.persist_directory, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Fusion360 API Documentation"},
        )

    def add_chunks(self, chunks: list[Chunk]) -> None:
        if not chunks:
            return
        ids = [c.chunk_id for c in chunks]
        documents = [c.content for c in chunks]
        metadatas = [
            {"title": c.title, "source_file": c.source_file, "api_type": c.api_type,
             "method_name": c.method_name, "property_type": c.property_type,
             "heading_level": c.heading_level, "version": c.version}
            for c in chunks
        ]
        self.collection.upsert(ids=ids, documents=documents, metadatas=metadatas)

    def query(self, query_text: str, top_k: int = 5) -> list[QueryResult]:
        results = self.collection.query(query_texts=[query_text], n_results=top_k)
        query_results = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i]
                chunk = Chunk(
                    chunk_id=results["ids"][0][i], content=doc,
                    title=metadata.get("title", ""), source_file=metadata.get("source_file", ""),
                    api_type=metadata.get("api_type", ""), method_name=metadata.get("method_name"),
                    property_type=metadata.get("property_type"),
                    heading_level=metadata.get("heading_level", 1), version=metadata.get("version"),
                )
                distance = results["distances"][0][i] if "distances" in results else 0.0
                query_results.append(QueryResult(chunk=chunk, distance=distance))
        return query_results

    def get_by_class(self, class_name: str) -> list[Chunk]:
        results = self.collection.get(where={"title": {"$eq": class_name}})
        chunks = []
        if results["documents"]:
            for i, doc in enumerate(results["documents"]):
                metadata = results["metadatas"][i]
                chunks.append(Chunk(
                    chunk_id=results["ids"][i], content=doc, title=metadata.get("title", ""),
                    source_file=metadata.get("source_file", ""), api_type=metadata.get("api_type", ""),
                    method_name=metadata.get("method_name"), property_type=metadata.get("property_type"),
                    heading_level=metadata.get("heading_level", 1), version=metadata.get("version"),
                ))
        return chunks

    def get_examples(self, class_name: str, method_name: Optional[str] = None) -> list[Chunk]:
        where_clause = {"title": {"$eq": class_name}, "api_type": {"$eq": "example"}}
        if method_name:
            where_clause["method_name"] = {"$eq": method_name}
        results = self.collection.get(where=where_clause)
        chunks = []
        if results["documents"]:
            for i, doc in enumerate(results["documents"]):
                metadata = results["metadatas"][i]
                chunks.append(Chunk(
                    chunk_id=results["ids"][i], content=doc, title=metadata.get("title", ""),
                    source_file=metadata.get("source_file", ""), api_type=metadata.get("api_type", ""),
                    method_name=metadata.get("method_name"), property_type=metadata.get("property_type"),
                    heading_level=metadata.get("heading_level", 1), version=metadata.get("version"),
                ))
        return chunks

    def list_classes(self, filter: Optional[str] = None) -> list[str]:
        results = self.collection.get()
        classes = set()
        if results["metadatas"]:
            for metadata in results["metadatas"]:
                title = metadata.get("title", "")
                if title and (filter is None or filter.lower() in title.lower()):
                    classes.add(title)
        return sorted(list(classes))

    def get_count(self) -> int:
        return self.collection.count()

    def reset(self) -> None:
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name, metadata={"description": "Fusion360 API Documentation"},
        )
