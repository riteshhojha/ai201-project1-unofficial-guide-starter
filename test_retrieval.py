from embedding import ChunksEmbedder


def test_retrieval():
    """Test retrieval with evaluation plan questions."""
    embedder = ChunksEmbedder()
    embedder.load_model()
    embedder.load_chunks()
    embedder.client = __import__("chromadb").PersistentClient(path=embedder.DB_PATH)
    embedder.collection = embedder.client.get_collection(name=embedder.COLLECTION_NAME)

    # Test questions from planning.md
    test_questions = [
        "What do students say about professor quality and workload at Allegheny?",
        "What are the main complaints about campus life and social environment?",
        "How affordable is this college according to student reviews?",
    ]

    for q_idx, question in enumerate(test_questions, 1):
        print(f"\n{'=' * 80}")
        print(f"QUERY {q_idx}: {question}")
        print(f"{'=' * 80}\n")

        results = embedder.retrieve(question, top_k=8)

        for rank, result in enumerate(results, 1):
            print(
                f"[{rank}] Distance: {result['distance']:.4f} | Source: {result['source']}"
            )
            print(f"    Text: {result['text'][:120]}...")
            print()

        # Relevance assessment
        avg_distance = sum(r["distance"] for r in results) / len(results)
        print(f"Average distance: {avg_distance:.4f}")
        print(f"{'✓ GOOD RETRIEVAL' if avg_distance < 0.5 else '⚠ CHECK RETRIEVAL'}")


if __name__ == "__main__":
    test_retrieval()
