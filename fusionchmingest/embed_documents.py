import platform
from dataclasses import dataclass
from typing import Optional

try:
    import numpy as np
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    np = None
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    SentenceTransformer = None
    torch = None
    TORCH_AVAILABLE = False

from fusionchmingest.vector_store import Chunk

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
FALLBACK_MODEL = "sentence-transformers/all-mpnet-base-v2"
BATCH_SIZE = 32

def get_device() -> str:
    if not TORCH_AVAILABLE:
        return "cpu"
    if platform.system() == "Darwin" and platform.machine() == "arm64":
        if torch.backends.mps.is_available():
            return "mps"
    return "cpu"

@dataclass
class ChunkWithEmbedding:
    chunk: Chunk
    embedding: np.ndarray

class EmbeddingEngine:
    def __init__(self, model_name: str = MODEL_NAME, device: Optional[str] = None, batch_size: int = BATCH_SIZE):
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError("sentence-transformers is required. Install with: pip install sentence-transformers")
        self.model_name = model_name
        self.device = device or get_device()
        self.batch_size = batch_size
        self.model = None

    def load_model(self) -> SentenceTransformer:
        if self.model is not None:
            return self.model
        try:
            self.model = SentenceTransformer(self.model_name, device=self.device)
        except Exception as e:
            print(f"Failed to load {self.model_name}: {e}")
            self.model = SentenceTransformer(FALLBACK_MODEL, device=self.device)
        return self.model

    def generate_embedding(self, text: str) -> np.ndarray:
        model = self.load_model()
        return model.encode(text, convert_to_numpy=True)

    def embed_chunks(self, chunks: list[Chunk]) -> list[ChunkWithEmbedding]:
        if not chunks:
            return []
        texts = [chunk.content for chunk in chunks]
        model = self.load_model()
        embeddings = model.encode(texts, batch_size=self.batch_size, show_progress_bar=True, convert_to_numpy=True)
        return [ChunkWithEmbedding(chunk=chunk, embedding=embedding) for chunk, embedding in zip(chunks, embeddings)]

def create_default_embedding_engine() -> EmbeddingEngine:
    return EmbeddingEngine()

def embed_chunks(chunks: list[Chunk]) -> list[ChunkWithEmbedding]:
    engine = create_default_embedding_engine()
    return engine.embed_chunks(chunks)
