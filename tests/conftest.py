import json
import os
import tempfile
import pytest
from pathlib import Path


FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir():
    return FIXTURES_DIR


@pytest.fixture
def sample_markdown():
    return FIXTURES_DIR / "sample.md"


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def vector_store_path(temp_dir):
    return os.path.join(temp_dir, "vectorstore")


@pytest.fixture
def sample_chunks():
    from fusionchmingest.vector_store import Chunk
    
    return [
        Chunk(
            chunk_id="test_1",
            content="# Feature class\n\nThe Feature class is the base class.",
            title="Feature class",
            source_file="Feature.md",
            api_type="class",
            method_name=None,
            property_type=None,
            heading_level=1,
            version="test",
        ),
        Chunk(
            chunk_id="test_2",
            content="## Methods\n\n### delete()\n\nDeletes the feature.",
            title="delete",
            source_file="Feature.md",
            api_type="method",
            method_name="delete",
            property_type=None,
            heading_level=2,
            version="test",
        ),
    ]
