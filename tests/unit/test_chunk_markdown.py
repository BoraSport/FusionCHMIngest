import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fusionchmingest.chunk_markdown import (
    count_tokens,
    extract_heading_level,
    extract_title_from_content,
    extract_api_info,
    split_by_headings,
    chunk_markdown_file,
    process_all_markdown_files,
)


class TestCountTokens:
    def test_count_simple_text(self):
        text = "Hello world"
        count = count_tokens(text)
        assert count == 2

    def test_count_empty_string(self):
        count = count_tokens("")
        assert count == 0


class TestExtractHeadingLevel:
    def test_h1(self):
        level = extract_heading_level("# Heading")
        assert level == 1

    def test_h2(self):
        level = extract_heading_level("## Heading")
        assert level == 2

    def test_not_heading(self):
        level = extract_heading_level("Regular text")
        assert level is None


class TestExtractTitleFromContent:
    def test_first_h1(self):
        content = "# Feature class\n\n## Description\n\nSome content"
        title = extract_title_from_content(content)
        assert title == "Feature class"

    def test_no_headings(self):
        content = "Just some text without headings"
        title = extract_title_from_content(content)
        assert title == ""


class TestExtractApiInfo:
    def test_class_only(self):
        class_name, method = extract_api_info("Feature")
        assert class_name == "Feature"

    def test_class_with_method(self):
        class_name, method = extract_api_info("Feature.delete")
        assert class_name == "Feature"
        assert method == "delete"


class TestSplitByHeadings:
    def test_split_single_heading(self):
        content = "# Title\n\nSome content here"
        chunks = split_by_headings(content)
        assert len(chunks) == 1


class TestChunkMarkdownFile:
    def test_chunk_file(self, sample_markdown):
        chunks = chunk_markdown_file(str(sample_markdown), version="test")
        assert len(chunks) > 0
        assert all(hasattr(c, 'chunk_id') for c in chunks)


class TestProcessAllMarkdownFiles:
    def test_process_directory(self, temp_dir, fixtures_dir):
        import shutil
        test_dir = os.path.join(temp_dir, "md_test")
        os.makedirs(test_dir)
        shutil.copy(fixtures_dir / "sample.md", os.path.join(test_dir, "test.md"))
        chunks = process_all_markdown_files(test_dir, version="test")
        assert len(chunks) > 0

    def test_process_nonexistent_directory(self):
        with pytest.raises(ValueError):
            process_all_markdown_files("/nonexistent/path")
