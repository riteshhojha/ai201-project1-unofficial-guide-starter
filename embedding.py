import json
import os
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple


class ChunksEmbedder:
    MODEL_NAME = "all-MiniLM-L6-v2"
    COLLECTION_NAME = "college_reviews"
    DB_PATH = "./chroma_db"

    def __init__(self, chunks_file: str = "chunks.json"):
        self.chunks_file = chunks_file
        self.model = None
        self.client = None
        self.collection = None
        self.chunks = []

    def load_model(self):
        """Load the embedding model."""
        print(f"Loading {self.MODEL_NAME}...")
        self.model = SentenceTransformer(self.MODEL_NAME)
        print(
            f"✓ Model loaded (dimension: {self.model.get_sentence_embedding_dimension()})"
        )

    def load_chunks(self):
        """Load chunks from JSON."""
        with open(self.chunks_file, "r") as f:
            self.chunks = json.load(f)
        print(f"✓ Loaded {len(self.chunks)} chunks")

    def setup_chromadb(self, reset: bool = False):
        """Initialize ChromaDB client and collection."""
        db_path = Path(self.DB_PATH)

        if reset and db_path.exists():
            import shutil

            shutil.rmtree(db_path)
            print(f"✓ Reset ChromaDB at {db_path}")

        self.client = chromadb.PersistentClient(path=self.DB_PATH)

        # Delete collection if it exists (for fresh start)
        try:
            self.client.delete_collection(name=self.COLLECTION_NAME)
            print(f"✓ Deleted existing collection")
        except:
            pass

        self.collection = self.client.create_collection(
            name=self.COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
        )
        print(f"✓ Created ChromaDB collection: {self.COLLECTION_NAME}")

    def embed_and_store(self, batch_size: int = 32):
        """Embed chunks and store in ChromaDB."""
        print(f"\nEmbedding {len(self.chunks)} chunks...")

        texts = [c["text"] for c in self.chunks]
        embeddings = self.model.encode(
            texts, batch_size=batch_size, show_progress_bar=True
        )

        print(f"✓ Generated {len(embeddings)} embeddings")

        # Prepare data for ChromaDB
        ids = []
        metadatas = []
        documents = []

        for idx, (chunk, embedding) in enumerate(zip(self.chunks, embeddings)):
            chunk_id = f"{chunk['source']}_{chunk['metadata']['chunk_id']}"
            ids.append(chunk_id)
            documents.append(chunk["text"])
            metadatas.append(
                {
                    "source": chunk["source"],
                    "chunk_id": str(chunk["metadata"]["chunk_id"]),
                    "length": str(chunk["metadata"]["length"]),
                }
            )

        # Store in ChromaDB
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings.tolist(),
            documents=documents,
            metadatas=metadatas,
        )

        print(f"✓ Stored {len(ids)} chunks in ChromaDB")

    def retrieve(self, query: str, top_k: int = 8, where: Dict = None) -> List[Dict]:
        """Retrieve top-k most relevant chunks for a query.

        Optional `where` is a ChromaDB metadata filter, e.g.
        {"source": "niche_sample"} or {"source": {"$in": ["reddit", "reddit_2"]}}.
        """
        query_embedding = self.model.encode(query)

        query_kwargs = {
            "query_embeddings": [query_embedding.tolist()],
            "n_results": top_k,
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            query_kwargs["where"] = where

        results = self.collection.query(**query_kwargs)

        # Format results
        retrieved = []
        for i in range(len(results["documents"][0])):
            retrieved.append(
                {
                    "text": results["documents"][0][i],
                    "source": results["metadatas"][0][i]["source"],
                    "chunk_id": results["metadatas"][0][i]["chunk_id"],
                    "distance": results["distances"][0][i],  # lower is better (cosine)
                }
            )

        return retrieved

    def run(self, reset: bool = False):
        """Run full embedding pipeline."""
        self.load_model()
        self.load_chunks()
        self.setup_chromadb(reset=reset)
        self.embed_and_store()
        print("\n✅ Embedding pipeline complete")


if __name__ == "__main__":
    embedder = ChunksEmbedder()
    embedder.run(reset=True)
