import os
from typing import Dict, List
from dotenv import load_dotenv
from groq import Groq
from embedding import ChunksEmbedder
import json

load_dotenv()


class GroundedGenerator:
    """Generate grounded answers using retrieval + Groq LLM."""

    MODEL = "llama-3.3-70b-versatile"

    SYSTEM_PROMPT = """You are a helpful assistant answering questions about student experiences at Allegheny College.

You MUST answer ONLY using the information provided in the retrieved documents below.
If the documents don't contain enough information to answer the question, explicitly say:
"I don't have enough information in the provided documents to answer that question."

DO NOT use your general knowledge or training data.
DO NOT make up information.

Always cite which document(s) your answer came from.
Format: "According to [source name]: [answer]"

Retrieved documents:
{context}

Remember: Answer ONLY from these documents. If information is missing, say so."""

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not set in .env")

        self.client = Groq(api_key=self.api_key)
        self.embedder = ChunksEmbedder()
        self.embedder.load_model()
        self.embedder.load_chunks()

        # Load ChromaDB collection
        import chromadb

        self.embedder.client = chromadb.PersistentClient(path=self.embedder.DB_PATH)
        self.embedder.collection = self.embedder.client.get_collection(
            name=self.embedder.COLLECTION_NAME
        )

    def available_sources(self) -> List[str]:
        """Return sorted list of distinct source documents in the vector store."""
        data = self.embedder.collection.get(include=["metadatas"])
        sources = {m["source"] for m in data["metadatas"]}
        return sorted(sources)

    @staticmethod
    def _build_where(source_filter) -> Dict:
        """Build a ChromaDB metadata filter from a source name or list of names."""
        if not source_filter:
            return None
        if isinstance(source_filter, str):
            source_filter = [source_filter]
        if len(source_filter) == 1:
            return {"source": source_filter[0]}
        return {"source": {"$in": list(source_filter)}}

    def retrieve_context(
        self, query: str, top_k: int = 8, source_filter=None
    ) -> tuple[str, List[Dict]]:
        """Retrieve context and format it for the prompt."""
        results = self.embedder.retrieve(
            query, top_k=top_k, where=self._build_where(source_filter)
        )

        # Format context
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(
                f"[Document {i} - {result['source']}]:\n{result['text']}"
            )

        context = "\n\n".join(context_parts)
        return context, results

    def generate(self, query: str, top_k: int = 8, source_filter=None) -> Dict:
        """Generate grounded answer for a query."""
        # Retrieve context
        context, retrieved_chunks = self.retrieve_context(
            query, top_k=top_k, source_filter=source_filter
        )

        # Prepare prompt
        system_prompt = self.SYSTEM_PROMPT.format(context=context)

        # Call Groq API
        completion = self.client.chat.completions.create(
            model=self.MODEL,
            max_tokens=1024,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
        )

        answer = completion.choices[0].message.content

        # Extract sources from retrieved chunks
        sources = list(set(c["source"] for c in retrieved_chunks))

        return {
            "query": query,
            "answer": answer,
            "sources": sources,
            "retrieved_chunks": retrieved_chunks,
        }

    def query(self, question: str) -> Dict:
        """User-facing query method."""
        print(f"\n{'=' * 80}")
        print(f"Question: {question}")
        print(f"{'=' * 80}\n")

        result = self.generate(question)

        print("Answer:")
        print(result["answer"])
        print(f"\nSources: {', '.join(result['sources'])}")
        print(f"Retrieval distance scores:")
        for i, chunk in enumerate(result["retrieved_chunks"][:3], 1):
            print(f"  {i}. {chunk['source']}: {chunk['distance']:.4f}")

        return result


if __name__ == "__main__":
    generator = GroundedGenerator()

    # Test queries
    test_queries = [
        "What do students say about professor quality and workload?",
        "How affordable is Allegheny College?",
        "What is the best pizza place near campus?",  # Should say "don't know"
    ]

    for question in test_queries:
        result = generator.query(question)
