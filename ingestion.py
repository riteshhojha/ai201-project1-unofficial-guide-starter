import os
import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Chunk:
    text: str
    source: str
    source_index: int
    chunk_index: int

    def to_dict(self) -> Dict:
        return {
            "text": self.text,
            "source": self.source,
            "source_index": self.source_index,
            "chunk_index": self.chunk_index,
            "metadata": {
                "source": self.source,
                "source_id": self.source_index,
                "chunk_id": self.chunk_index,
                "length": len(self.text),
            }
        }


class DocumentIngestion:
    CHUNK_SIZE = 300
    OVERLAP = 50
    DOCUMENTS_DIR = "documents"

    def __init__(self, documents_dir: str = None):
        self.documents_dir = Path(documents_dir or self.DOCUMENTS_DIR)
        self.documents = {}
        self.chunks: List[Chunk] = []

    def load_documents(self) -> Dict[str, str]:
        """Load all .txt files from documents directory."""
        if not self.documents_dir.exists():
            raise FileNotFoundError(f"Directory {self.documents_dir} not found")

        txt_files = sorted(self.documents_dir.glob("*.txt"))
        if not txt_files:
            raise FileNotFoundError(f"No .txt files found in {self.documents_dir}")

        for file_path in txt_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    self.documents[file_path.stem] = content
                    print(f"✓ Loaded {file_path.name} ({len(content)} chars)")
            except Exception as e:
                print(f"✗ Error loading {file_path.name}: {e}")

        print(f"\nLoaded {len(self.documents)} documents")
        return self.documents

    def clean_text(self, text: str) -> str:
        """Clean document text."""
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\n+', '\n', text)
        return text

    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        chunks = []
        start = 0

        while start < len(text):
            end = min(start + self.CHUNK_SIZE, len(text))
            chunk = text[start:end]

            if chunk.strip():
                chunks.append(chunk)

            if end >= len(text):
                break

            start += self.CHUNK_SIZE - self.OVERLAP

        return chunks

    def ingest_and_chunk(self) -> List[Chunk]:
        """Load documents, clean, and chunk with source attribution."""
        self.load_documents()

        source_index = 0
        for source_name in sorted(self.documents.keys()):
            text = self.documents[source_name]
            cleaned = self.clean_text(text)

            chunks = self.chunk_text(cleaned)

            for chunk_index, chunk_text in enumerate(chunks):
                chunk = Chunk(
                    text=chunk_text,
                    source=source_name,
                    source_index=source_index,
                    chunk_index=chunk_index,
                )
                self.chunks.append(chunk)

            print(f"  {source_name}: {len(chunks)} chunks")
            source_index += 1

        print(f"\nTotal chunks: {len(self.chunks)}")
        return self.chunks

    def get_chunk_stats(self) -> Dict:
        """Return chunking statistics."""
        if not self.chunks:
            return {}

        chunk_lengths = [len(c.text) for c in self.chunks]
        return {
            "total_chunks": len(self.chunks),
            "avg_chunk_size": sum(chunk_lengths) / len(chunk_lengths),
            "min_chunk_size": min(chunk_lengths),
            "max_chunk_size": max(chunk_lengths),
            "total_text_length": sum(chunk_lengths),
            "unique_sources": len(self.documents),
        }

    def save_chunks_json(self, output_file: str = "chunks.json"):
        """Save chunks to JSON file."""
        import json
        chunks_data = [c.to_dict() for c in self.chunks]
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(chunks_data, f, indent=2)
        print(f"✓ Saved {len(chunks_data)} chunks to {output_file}")

    def save_chunks_tsv(self, output_file: str = "chunks.tsv"):
        """Save chunks to TSV for inspection."""
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("source\tchunk_index\ttext\tlength\n")
            for chunk in self.chunks:
                text_safe = chunk.text.replace("\n", " ").replace("\t", " ")
                f.write(f"{chunk.source}\t{chunk.chunk_index}\t{text_safe}\t{len(chunk.text)}\n")
        print(f"✓ Saved {len(self.chunks)} chunks to {output_file}")


if __name__ == "__main__":
    ingestion = DocumentIngestion()

    chunks = ingestion.ingest_and_chunk()
    stats = ingestion.get_chunk_stats()

    print("\n=== Chunking Statistics ===")
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"{key}: {value:.1f}")
        else:
            print(f"{key}: {value}")

    print("\n=== Sample Chunks ===")
    for i, chunk in enumerate(chunks[:3]):
        print(f"\n[{i}] Source: {chunk.source}")
        print(f"    Text: {chunk.text[:100]}...")
        print(f"    Length: {len(chunk.text)} chars")

    ingestion.save_chunks_json("chunks.json")
    ingestion.save_chunks_tsv("chunks.tsv")
