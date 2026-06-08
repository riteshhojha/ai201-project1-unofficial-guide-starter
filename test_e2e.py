"""End-to-end test of the grounded generation system."""

from generation import GroundedGenerator


def test_end_to_end():
    """Test full pipeline with all 5 evaluation questions."""
    generator = GroundedGenerator()

    evaluation_questions = [
        "What do students say about professor quality and workload at Allegheny?",
        "What are the main complaints about campus life and social environment?",
        "How affordable is this college according to student reviews?",
        "What do students say about internship and career support?",
        "Compare student satisfaction: how does this school rank among peer institutions?",
    ]

    results = []

    for i, question in enumerate(evaluation_questions, 1):
        print(f"\n{'=' * 80}")
        print(f"Q{i}: {question}")
        print(f"{'=' * 80}\n")

        result = generator.generate(question)

        print("Answer:")
        print(result["answer"])
        print(f"\nSources: {', '.join(result['sources'])}")
        print(
            f"Avg distance: {sum(c['distance'] for c in result['retrieved_chunks']) / len(result['retrieved_chunks']):.4f}"
        )

        results.append(
            {
                "question": question,
                "answer": result["answer"],
                "sources": result["sources"],
            }
        )

    return results


if __name__ == "__main__":
    print("🧪 Running end-to-end grounded generation test...\n")
    results = test_end_to_end()
    print(f"\n✅ Completed {len(results)} evaluation questions")
