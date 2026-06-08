"""Stretch feature: compare chunking strategies on the same query set.

Builds the corpus under several (chunk_size, overlap) settings, embeds each into
an in-memory ChromaDB collection with the same model, and runs the same 3
evaluation queries against each. Reports avg top-k cosine distance so we can see
which chunking strategy retrieves more relevant material.

Run: python chunking_comparison.py
"""

import chromadb
from sentence_transformers import SentenceTransformer

from ingestion import DocumentIngestion

MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 8

STRATEGIES = [
    (150, 30),   # fine-grained
    (300, 50),   # current production setting
    (600, 100),  # coarse-grained
]

QUERIES = [
    "What do students say about professor quality and workload at Allegheny?",
    "What are the main complaints about campus life and social environment?",
    "How affordable is this college according to student reviews?",
]


def build_chunks(chunk_size: int, overlap: int):
    ing = DocumentIngestion()
    ing.CHUNK_SIZE = chunk_size  # instance attr shadows class constant
    ing.OVERLAP = overlap
    chunks = ing.ingest_and_chunk()
    return [c.to_dict() for c in chunks]


def main():
    print(f"Loading {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)
    client = chromadb.EphemeralClient()

    summary = []  # (size, overlap, n_chunks, [avg per query], overall_avg)

    for size, overlap in STRATEGIES:
        print(f"\n{'#' * 70}\n# Strategy: {size} chars / {overlap} overlap\n{'#' * 70}")
        chunks = build_chunks(size, overlap)
        texts = [c["text"] for c in chunks]
        embeddings = model.encode(texts, show_progress_bar=False)

        coll_name = f"chunks_{size}_{overlap}"
        try:
            client.delete_collection(coll_name)
        except Exception:
            pass
        coll = client.create_collection(
            name=coll_name, metadata={"hnsw:space": "cosine"}
        )
        coll.add(
            ids=[f"{c['source']}_{c['chunk_index']}_{i}" for i, c in enumerate(chunks)],
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=[{"source": c["source"]} for c in chunks],
        )

        per_query = []
        for q in QUERIES:
            qe = model.encode(q)
            res = coll.query(
                query_embeddings=[qe.tolist()],
                n_results=TOP_K,
                include=["distances"],
            )
            dists = res["distances"][0]
            avg = sum(dists) / len(dists)
            best = min(dists)
            per_query.append(avg)
            print(f"  Q: {q[:50]}...  avg={avg:.4f}  best={best:.4f}")

        overall = sum(per_query) / len(per_query)
        summary.append((size, overlap, len(chunks), per_query, overall))
        print(f"  -> overall avg distance: {overall:.4f}")

    print(f"\n\n{'=' * 70}\nSUMMARY (lower distance = better retrieval)\n{'=' * 70}")
    header = f"{'size/overlap':>14} | {'#chunks':>7} | {'Q1':>7} | {'Q2':>7} | {'Q3':>7} | {'overall':>7}"
    print(header)
    print("-" * len(header))
    for size, overlap, n, pq, overall in summary:
        print(
            f"{f'{size}/{overlap}':>14} | {n:>7} | {pq[0]:>7.4f} | {pq[1]:>7.4f} | "
            f"{pq[2]:>7.4f} | {overall:>7.4f}"
        )


if __name__ == "__main__":
    main()
