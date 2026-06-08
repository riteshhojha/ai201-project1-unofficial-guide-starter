# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

College Student Reviews and Experiences — an aggregated database of authentic student perspectives on college life, academics, campus environment, and post-graduation outcomes. This knowledge is valuable because official college marketing materials don't capture teaching quality variance, workload reality, social dynamics, or true graduate outcomes. Students make $50K+ four-year commitments based on incomplete information; honest peer feedback fills that gap.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| #   | Source                     | Description                                                 | URL or location                          |
| --- | -------------------------- | ----------------------------------------------------------- | ---------------------------------------- |
| 1   | Allegheny Website Reviews  | Official college site + student testimonials                | documents/allegehny_website.txt          |
| 2   | CC Forum Discussions       | College Confidential forum threads on campus life           | documents/cc_forum.txt                   |
| 3   | Niche Reviews              | Aggregated student ratings on academics, social life, dorms | documents/niche_reviews.txt              |
| 4   | Niche Reviews (Friends)    | Additional Niche reviews from peer networks                 | documents/niche_reviews_friends.txt      |
| 5   | Reddit Thread 1            | r/college subreddit discussions on experiences              | documents/reddit.txt                     |
| 6   | Reddit Thread 2            | r/[college-specific] subreddit reviews                      | documents/reddit_2.txt                   |
| 7   | College Choice Rankings    | Comparative college rankings and sorting                    | documents/college_choice.txt             |
| 8   | College Confidential Forum | Community-sourced college planning advice (22M+ posts)      | documents/college_confidential_forum.txt |
| 9   | Best Colleges Reviews      | Expert-reviewed college comparisons and affordability data  | documents/best_colleges.txt              |
| 10  | Rate My Professors         | Professor-level ratings and course difficulty assessments   | documents/rate_my_professors.txt         |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** 300 characters (~75 tokens)

**Overlap:** 50 characters (20% overlap)

**Reasoning:** Review-heavy corpus with short, focused opinions. Smaller chunks capture individual review statements without losing context. 300 chars preserves complete thoughts (e.g., "Professor X is engaging but grades harshly, expect 2-3 hours homework daily"). Overlap prevents splitting key review phrases across boundaries.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** all-MiniLM-L6-v2 (via sentence-transformers) — lightweight, fast, fine-tuned on semantic similarity

**Top-k:** 8 chunks per query

**Production tradeoff reflection:** For production, I'd weigh accuracy vs. cost/latency. Larger models like OpenAI's text-embedding-3-large offer better domain understanding but add API costs + latency. For college reviews, nuance matters (slang, colloquialisms like "weeder class"); a larger model would reduce false positives. I'd also consider multilingual support if international student perspectives were in scope. LocalGPT embedding models avoid vendor lock-in but require GPU hosting.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| #   | Question                                                                         | Expected answer                                                                                                                                   |
| --- | -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | What do students say about professor quality and workload at Allegheny?          | Mix of responses covering professor accessibility, grading fairness, homework volume; specific examples from Rate My Professors or Reddit threads |
| 2   | What are the main complaints about campus life and social environment?           | References to dorm quality, dining, social scene accessibility, inclusivity issues across multiple source perspectives                            |
| 3   | How affordable is this college according to student reviews?                     | Financial aid experiences, hidden costs, part-time job necessity; sourced from Best Colleges affordability data + student forum discussions       |
| 4   | What do students say about internship and career support?                        | Post-graduation outcomes, recruiting presence, career services quality mentioned in College Confidential or Reddit discussions                    |
| 5   | Compare student satisfaction: how does this school rank among peer institutions? | Comparative sentiment across Niche ratings, Best Colleges rankings, and peer school discussions                                                   |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. **Sentiment fragmentation across chunk boundaries:** College reviews often express nuanced opinions ("Good professors but hard grading" or "Great social scene but limited academics"). Splitting at 300 chars may sever sentiment modifiers from their subjects, causing retrieval to miss contradictory viewpoints and leading to one-sided answers.

2. **Source mixing and contradiction:** Multiple sources contradict each other (Niche ratings may be higher than Reddit complaints). Without clear source attribution in chunks, the model may hallucinate consensus where none exists. Risk: system claims unanimity when sources show splits by class year, major, or demographic.

3. **Temporal staleness:** Forum posts and reviews can be years old; curriculum changes, professors retire, but outdated reviews remain in retrieval. System may answer with 2019 data in 2026, missing recent improvements or declines.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

```
┌─────────────────────┐
│  Document Ingestion │
│   (read .txt files  │
│   from /documents)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│     Chunking        │
│ (300 char chunks,   │
│  50 char overlap,   │
│  Python string ops) │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Embedding + Store   │
│ (all-MiniLM-L6-v2   │
│  via sentence-      │
│  transformers →     │
│  ChromaDB vector    │
│  store)             │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    Retrieval        │
│ (semantic search,   │
│  top-k=8 chunks)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    Generation       │
│ (Claude API +       │
│  system prompt for  │
│  grounding +        │
│  source attribution)│
└─────────────────────┘
```

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**
- **Tool:** Claude (Code)
- **Input:** Chunking Strategy section (300 chars, 50 char overlap), sample review text from documents/
- **Expected output:** Python `chunk_text()` function that respects size/overlap, preserves complete review statements
- **Verification:** Test on 5 sample reviews; manually verify chunks don't split mid-sentence and overlap correctly

**Milestone 4 — Embedding and retrieval:**
- **Tool:** Claude
- **Input:** Retrieval Approach section (all-MiniLM-L6-v2, top-k=8), ChromaDB integration requirements
- **Expected output:** Python functions for embedding chunks, storing in ChromaDB, querying by semantic similarity
- **Verification:** Embed 100 chunks, run 3 test queries, verify top-8 results match review topics

**Milestone 5 — Generation and interface:**
- **Tool:** Claude
- **Input:** Evaluation Plan questions, grounding requirements, expected answer structure
- **Expected output:** System prompt for Claude API that enforces grounding + Python interface to tie retrieval→generation
- **Verification:** Run 5 test questions through system; manually score retrieval quality and response accuracy using Evaluation Report table
