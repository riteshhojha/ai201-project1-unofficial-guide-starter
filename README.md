# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

**College Student Reviews and Experiences** — An aggregated knowledge base of authentic student perspectives on Allegheny College, covering academics, campus life, social environment, affordability, and post-graduation outcomes.

**Why this knowledge is valuable:** Official college marketing materials and course catalogs don't capture teaching quality variance, actual workload, social dynamics, or honest graduate outcomes. Students commit $50K+ for a four-year degree based on incomplete information. Peer-generated reviews fill this gap by providing unfiltered perspectives on what the college experience is actually like — which professors are effective, which are difficult, what the housing lottery is really like, whether financial aid packages are generous, and what students actually do after graduation.

**Why it's hard to find officially:** Colleges control their official narratives and aren't incentivized to publish negative feedback. Student reviews are scattered across dozens of platforms (Rate My Professors, Niche, Reddit, College Confidential forums) with different formats, review densities, and update frequencies. No single authoritative source aggregates honest, searchable student feedback.

---

## Document Sources

| #   | Source                         | Type                           | URL or file path                         |
| --- | ------------------------------ | ------------------------------ | ---------------------------------------- |
| 1   | Allegheny Official Website     | Institutional content          | documents/allegheny_website.txt          |
| 2   | College Confidential Forum     | Forum discussions              | documents/cc_forum.txt                   |
| 3   | Niche Reviews                  | Aggregated ratings             | documents/niche_reviews.txt              |
| 4   | Niche Reviews (Friends)        | Peer network reviews           | documents/niche_reviews_friends.txt      |
| 5   | Reddit r/college               | Subreddit discussions          | documents/reddit.txt                     |
| 6   | Reddit r/pittsburgh            | Subreddit discussions          | documents/reddit_2.txt                   |
| 7   | College Choice                 | Ranking platform               | documents/college_choice.txt             |
| 8   | College Confidential Community | 22M+ posts on college planning | documents/college_confidential_forum.txt |
| 9   | Best Colleges                  | Expert-reviewed rankings       | documents/best_colleges.txt              |
| 10  | Rate My Professors             | Professor ratings              | documents/rate_my_professors.txt         |

---

## Chunking Strategy

**Chunk size:** 300 characters (~75 tokens)

**Overlap:** 50 characters (20% overlap)

**Why these choices fit your documents:** The corpus is review-heavy with short, focused opinions — individual reviews are typically 1–3 sentences. A 300-character chunk preserves complete review thoughts (e.g., "Professor X is engaging but grades harshly, expect 2-3 hours homework daily") without diluting context. Smaller chunks would fragment opinions across boundaries, making retrieval miss nuanced viewpoints. The 50-character overlap (20%) prevents key phrases from being split across chunk boundaries and helps the embedding model see semantic continuity.

**Preprocessing:** Documents were cleaned to remove whitespace-only lines, normalize multiple newlines to single newlines, and strip leading/trailing whitespace. No HTML tags were present in the final documents (source metadata headers were preserved as they provide context).

**Final chunk count:** 64 chunks across 10 original sources (13 total with sample/generated review files)

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` (via `sentence-transformers`)

**Why this choice:** MiniLM is a lightweight, distilled model fine-tuned for semantic similarity tasks. It runs locally on CPU with no API keys or rate limits, making it ideal for development and evaluation. With 384 dimensions, it strikes a balance between semantic expressiveness and computational efficiency. For college reviews — where nuance matters (slang like "weeder class," specific professor names, subjective opinions) — MiniLM's general-domain training is sufficient.

**Production tradeoff reflection:** In production with unlimited cost, I'd weigh several alternatives:
- **Larger models** (OpenAI's `text-embedding-3-large`, Cohere's embed-v3-large): Better domain-specific accuracy and handling of synonyms/paraphrases, but higher latency and API costs ($0.13 per 1M tokens). Worth it if accuracy gains matter more than cost.
- **Domain-specific fine-tuning:** Train an embedding model on Allegheny reviews to capture college-specific terminology. High upfront cost, but improves retrieval precision for this specific use case.
- **Multilingual support:** If expanding to international student reviews, models like `multilingual-e5-base` handle 100+ languages but add computational overhead.
- **Local vs. API:** Running locally (MiniLM) avoids data privacy concerns; API-hosted models offer better accuracy but introduce latency and vendor lock-in.

For this project, MiniLM's speed, local availability, and reasonable accuracy make it the right choice.

---

## Grounded Generation

**System prompt grounding instruction:**

```
You are a helpful assistant answering questions about student experiences at Allegheny College.

You MUST answer ONLY using the information provided in the retrieved documents below.
If the documents don't contain enough information to answer the question, explicitly say:
"I don't have enough information in the provided documents to answer that question."

DO NOT use your general knowledge or training data.
DO NOT make up information.

Always cite which document(s) your answer came from.
Format: "According to [source name]: [answer]"

Retrieved documents:
{context}

Remember: Answer ONLY from these documents. If information is missing, say so.
```

**Mechanism:** Grounding is enforced through three layers:
1. **System message** (shown above) is placed before the user query in the LLM's message history, making it the primary instruction the model sees.
2. **Context injection**: Retrieved chunks are formatted with source attribution and inserted directly into the system message. The model sees these documents as its *only* knowledge source for this query.
3. **Source attribution in response:** The model is instructed to cite sources using the "According to [source]:" format. This makes hallucination detectable — if the model cites a non-existent source or attributes an answer to a document that doesn't contain that information, it's immediately visible to the user.

**How source attribution is surfaced:** Every response includes:
1. **Inline citations:** The model cites source names (e.g., "sample_reviews") in the answer text itself.
2. **Source list UI:** The Gradio interface displays retrieved sources and their relevance scores (cosine distance) below the answer, making the retrieval transparent.
3. **Verifiability:** Users can inspect which documents were retrieved and confirm the answer is traceable to those documents.

---

## Evaluation Report

| #   | Question                                                                         | Expected answer                                                                                                                                   | System response (summarized)                                                                                                                                                                         | Retrieval quality  | Response accuracy  |
| --- | -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------ | ------------------ |
| 1   | What do students say about professor quality and workload?                       | Mix of responses covering professor accessibility, grading fairness, homework volume; specific examples from Rate My Professors or Reddit threads | Professor Miller is engaging with fair grading and 3-4 hrs/week homework. Biology prof has poor delivery, unfair exams. Chemistry has harsh grading but good labs. Workload is heavy but manageable. | Relevant           | Accurate           |
| 2   | What are the main complaints about campus life and social environment?           | References to dorm quality, dining, social scene accessibility, inclusivity issues across multiple source perspectives                            | Housing lottery frustrating, dining mediocre, social circles cliquey, parking awful, WiFi inconsistent, some areas poorly lit at night. LGBTQ+ community present but navigating inclusion.           | Relevant           | Accurate           |
| 3   | How affordable is this college according to student reviews?                     | Financial aid experiences, hidden costs, part-time job necessity; sourced from Best Colleges affordability data + student forum discussions       | College is expensive with wide variation in financial aid. Out-of-state costs high. Merit scholarships competitive. Many students work part-time. Cost-benefit depends on aid package.               | Relevant           | Accurate           |
| 4   | What do students say about internship and career support?                        | Post-graduation outcomes, recruiting presence, career services quality mentioned in College Confidential or Reddit discussions                    | Strong internship recruiting in finance and tech, weaker in humanities. Career services helpful but understaffed. Tech jobs paid 70-90k starting salary. Alumni network strong in coastal cities.    | Partially relevant | Partially accurate |
| 5   | Compare student satisfaction: how does this school rank among peer institutions? | Comparative sentiment across Niche ratings, Best Colleges rankings, and peer school discussions                                                   | Overall rating 4.2/5 stars. Academics 4.5/5, dorms 3.2/5, food 2.9/5, social scene 3.7/5. System correctly noted lack of peer comparisons in documents.                                              | Partially relevant | Partially accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

**Summary:** 3/5 queries returned highly accurate, well-grounded answers. Q4 and Q5 are partially accurate — the system retrieved relevant information but some nuance was lost due to limited coverage in the source documents (Q4 has less detail on humanities outcomes; Q5 lacks explicit peer comparisons).

---

## Failure Case Analysis

**Question that failed:** Q4: "What do students say about internship and career support?"

**What the system returned:** The system returned information that internship recruiting is "strong in finance and tech, weaker in humanities," and that career services is "helpful but understaffed." This is partially correct but missing key details about the breadth of outcomes. The model correctly retrieved career-related chunks but didn't capture nuanced perspectives on whether career services *actually* helps, or what percentage of graduates find jobs in their major.

**Root cause (tied to a specific pipeline stage):** **Retrieval limitation** — The chunks retrieved for this query were dominated by general career-support information from sample_reviews and reddit_reviews, which are relatively generic. The actual source documents (Rate My Professors, specific Reddit threads, Niche reviews) contain more specific graduate outcome data, but those chunks were ranked lower in retrieval because they use different vocabulary (e.g., "recruiting," "placement rates," "alumni network") than the query ("internship," "career support"). The semantic distance scores for top-4 results averaged 0.5–0.65, indicating weaker semantic match compared to Q1–Q3 (~0.46–0.51).

**What you would change to fix it:** 
1. **Augment source documents** with more detailed career outcome data (graduate placement rates, starting salaries by major, alumni testimonials about job search difficulty).
2. **Expand retrieval** to top-k=10 or 12 for career queries specifically, as this topic has more vocabulary variance and benefits from wider context.
3. **Add query expansion** — when the user asks about "internship support," also search for related terms like "recruiting," "placement," "alumni network," "job outcomes" in parallel and merge results.

---

## Spec Reflection

**One way the spec helped you during implementation:**

The **Chunking Strategy section** in planning.md was invaluable. By specifying chunk size (300 chars), overlap (50 chars), and reasoning *before* coding, I avoided the common RAG mistake of guessing at these values. When testing retrieval, I could trace poor results directly back to the spec and validate that the implementation matched it. The spec forced me to think about the trade-off between chunk size and retrieval precision upfront — small chunks risk fragmenting reviews, large chunks dilute specificity. Having this decision documented meant I could focus on debugging retrieval quality rather than second-guessing architectural choices.

**One way your implementation diverged from the spec, and why:**

The **vector store** implementation diverged slightly: planning.md mentioned ChromaDB but didn't specify persistent vs. in-memory storage. I chose **persistent storage** (writing to disk) to enable reuse across sessions and faster iteration during testing. This wasn't a breaking change but added operational complexity — I had to manage database cleanup and file permissions. In hindsight, for a RAG system that needs fast iteration, ephemeral in-memory storage might have been better during development, then switching to persistent for production. The spec didn't guide this operational decision, so I made it based on what seemed "right" rather than what was most practical for the project timeline.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:* I provided Claude with the Chunking Strategy section from planning.md (300 chars, 50 char overlap, reasoning), a description of the document types (text reviews), and asked it to implement a `chunk_text()` function that respects size and overlap while preserving complete review statements.
- *What it produced:* Claude generated a clean `DocumentIngestion` class with overlapping chunk splitting using character offsets, proper filtering of empty chunks, and source metadata tracking.
- *What I changed or overrode:* The implementation was mostly correct, but I added an extra check to skip chunks with only whitespace (`if chunk.strip()`), and I modified the batch processing to load *all* documents upfront rather than stream them, for faster experimentation.

**Instance 2**

- *What I gave the AI:* I provided the LLM pipeline diagram from planning.md, the grounding requirements ("answer only from retrieved documents"), and asked Claude to implement a system prompt that enforces grounding and includes source attribution. I also specified the output format should cite sources.
- *What it produced:* Claude generated a detailed system prompt with explicit instructions to decline answering if documents don't contain information, formatted context with source labels, and required citation format ("According to [source]:").
- *What I changed or overrode:* The system prompt was strong, but I had to debug the Groq API integration — Claude had used the OpenAI-style `system=` parameter, which Groq's chat.completions API doesn't support. I corrected this to include system message in the `messages` array instead. Also, I added explicit enforcement of source attribution in the response (the model naturally complies with the prompt, but I wanted to be defensive).
