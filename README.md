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

## Sample Chunks

Six representative chunks produced by the ingestion + chunking pipeline (`chunks.json`), each labeled with its source document. Chunks are 300 characters with 50-character overlap, which is why some begin mid-word — the overlap deliberately carries context across boundaries.

**Chunk 1 — source: `sample_reviews` (chunk_index 0)**
> # Sample College Reviews ## Professor Quality & Workload Professor Miller is engaging and knows the material well, but expects a lot from students. Exams are fairly graded and she gives partial credit generously. Expect 3-4 hours of homework per week for CS major courses. Students say her office hou

**Chunk 2 — source: `niche_sample` (chunk_index 0)**
> # Niche Student Reviews Overall Experience (4.2/5 stars): "Great school with strong academics but expensive. Financial aid varies widely. The campus is beautiful and safe. Community feel is strong if you get involved. Definitely worth visiting before applying - the tour doesn't capture the real vibe

**Chunk 3 — source: `reddit_reviews` (chunk_index 0)**
> # Reddit r/college Discussions Posted on r/college: "I'm a junior here and honestly the experience has been mixed. Great professors in my major but the administration is frustratingly slow. Course registration is a nightmare - I had to wake up at 6am on registration day to get the classes I need. Al

**Chunk 4 — source: `reddit_2` (chunk_index 0)**
> SOURCE: r/reddit URL: https://www.reddit.com/r/pittsburgh/comments/143n9y8/thoughts_on_allegheny_college/ Year: 2023 I would say it's great for getting into grad school and less so for getting a job, but everyone's situation is different and I wound up doing fine without grad school. Not sure how th

**Chunk 5 — source: `best_colleges` (chunk_index 2)**
> ce - Scholarship databases organized by student demographics - Articles on free tuition and low-cost degree programs Credibility: Cited by Forbes, NBC, Bloomberg, USA Today, NY Times; 40+ expert reviewers Key Insight: Expert-reviewed resource with emphasis on affordability and comprehensive program

**Chunk 6 — source: `rate_my_professors` (chunk_index 0)**
> Rate My Professors Reviews (ratemyprofessors.com) Source: www.ratemyprofessors.com Type: Professor and course review platform Description: Student-generated platform for rating and reviewing individual professors Features: - Search professors by school or name - Anonymous rating submissions - User a

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

## Retrieval Test Results

Retrieval was tested directly (`test_retrieval.py`) with top-k=8. Distances are cosine distance (lower = more similar). Below are the top returned chunks for three queries, followed by a relevance explanation for two of them.

### Query 1 — "What do students say about professor quality and workload at Allegheny?" (avg distance 0.5129)

| Rank | Distance | Source         | Chunk excerpt                                                                                              |
| ---- | -------- | -------------- | ---------------------------------------------------------------------------------------------------------- |
| 1    | 0.4664   | sample_reviews | "# Sample College Reviews ## Professor Quality & Workload Professor Miller is engaging and knows the material well, but e…" |
| 2    | 0.4807   | niche_sample   | "…tically in quality. Some juniors are in nice apartments, others in terrible converted buildings. Lottery system is frust…" |
| 3    | 0.4908   | reddit_2       | "SOURCE: r/reddit … Year: 2023 I would say it's great for getting into grad school and less so for getting a job…"          |
| 4    | 0.4997   | sample_reviews | "…for CS major courses. Students say her office hours are invaluable if you're struggling. The introductory biology profe…" |
| 5    | 0.5177   | niche_sample   | "…applying - the tour doesn't capture the real vibe." Academics (4.5/5 stars): "Professors genuinely care about teaching…"   |

**Why these are relevant:** Ranks 1, 4, and 5 directly address the query — they describe a named professor's grading/workload, intro-course teaching quality, and overall academic experience, which is exactly what "professor quality and workload" asks about. Ranks 2 and 3 are the weakest matches (housing quality, grad-school vs. jobs); they were pulled in because the query is broad and these chunks share academic-life vocabulary, but they're the reason the average distance (0.5129) sits at the threshold rather than well below it.

### Query 2 — "What are the main complaints about campus life and social environment?" (avg distance 0.4737)

| Rank | Distance | Source         | Chunk excerpt                                                                                              |
| ---- | -------- | -------------- | ---------------------------------------------------------------------------------------------------------- |
| 1    | 0.4210   | niche_sample   | "…tically in quality. Some juniors are in nice apartments, others in terrible converted buildings. Lottery system is frust…" |
| 2    | 0.4489   | niche_sample   | "…cost is significant. Consider alternatives if cost is your main concern. Worth the investment if you're getting good sup…" |
| 3    | 0.4682   | sample_reviews | "…esponsive to student concerns about housing and safety. Campus is well-lit and feels safe at night. Parking on campus is…" |
| 4    | 0.4690   | reddit_reviews | "…Campus is beautiful and feels safe during the day. At night some areas near the old science building are poorly lit…"      |
| 5    | 0.4711   | reddit_reviews | "…surroundings when leaving late events." Residential life review: "Freshman dorms are small but you make lifelong friend…"  |

**Why these are relevant:** Every top-5 chunk is on-topic for campus life — housing lottery quality (1), campus safety and parking (3, 4), and residential/dorm life (5). The cluster of low distances (0.42–0.47, avg 0.4737) reflects that complaints about housing, safety, and dorms are densely and explicitly covered in the corpus, so the embedding model finds tight matches. Rank 2 (cost/value) is the only mild drift and is still adjacent to the "is it worth it" sentiment students raise when complaining.

### Query 3 — "How affordable is this college according to student reviews?" (avg distance 0.4609)

| Rank | Distance | Source         | Chunk excerpt                                                                                              |
| ---- | -------- | -------------- | ---------------------------------------------------------------------------------------------------------- |
| 1    | 0.3440   | niche_sample   | "# Niche Student Reviews Overall Experience (4.2/5 stars): "Great school with strong academics but expensive. Financial a…" |
| 2    | 0.4032   | niche_sample   | "…cost is significant. Consider alternatives if cost is your main concern. Worth the investment if you're getting good sup…" |
| 3    | 0.4671   | niche_sample   | "…tically in quality. Some juniors are in nice apartments…"                                                  |
| 4    | 0.4804   | sample_reviews | "…ificantly better if you get into the good dorms. Housing lottery system is frustrating and unfair…"        |
| 5    | 0.4850   | niche_sample   | "…be cliquey. International student integration could be better." Value (3.4/5 stars): "Cost is high relative to some pee…" |

This query had the best retrieval of the three (top hit at 0.3440), because affordability is discussed using direct vocabulary ("expensive," "financial aid," "cost," "value") that the query mirrors closely.

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

## Example Responses

These are verbatim outputs from the running system. Source attribution ("According to [Document N - source]:") is visible inline in the answer text, and the interface additionally lists retrieved sources with distance scores.

**Example 1 — affordability (in-scope, well grounded)**

*Query:* "How affordable is this college according to student reviews?"

*Response:*
> According to [Document 1 - niche_sample]: The college is "expensive" and "Financial aid varies widely."
> According to [Document 2 - niche_sample]: The "cost is significant" and students should "Consider alternatives if cost is your main concern."
> According to [Document 5 - niche_sample]: The "Cost is high relative to some peer institutions" and "Out-of-state cost is significant."
> According to [Document 7 - reddit_reviews]: The college is "Expensive" and "financial aid wasn't generous."
>
> Overall, student reviews indicate that the college is not very affordable, with high costs and varying financial aid.

*Retrieved sources:* niche_sample, reddit_reviews, best_colleges, sample_reviews

**Example 2 — campus life (in-scope, well grounded)**

*Query:* "What are the main complaints about campus life and social environment?"

*Response (excerpt):*
> According to [Document 1 - niche_sample]: The main complaints include the lottery system for housing being frustrating, and the dining hall quality being below average…
> According to [Document 3 - sample_reviews]: Parking on campus is nearly impossible…
> According to [Document 4 - reddit_reviews]: Some areas near the old science building are poorly lit at night, and there were incidents of parking lot assaults…
> According to [Document 6 - niche_sample]: …social circles being cliquey, and it requires effort to have a non-alcoholic social life.

*Retrieved sources:* niche_sample, sample_reviews, reddit_reviews

**Example 3 — out-of-scope query (refusal)**

*Query:* "What is the best pizza place near campus?"

*Response:*
> I don't have enough information in the provided documents to answer that question.

The retrieved chunks (from niche_sample, reddit_reviews, etc.) contain no restaurant/food-recommendation content, so the grounding instruction correctly triggers the refusal template instead of the model falling back on general knowledge.

---

## Query Interface

The interface is a Gradio web app (`app.py`), launched with `python app.py`.

**Input field:**
- **Your Question** — a multi-line textbox where the user types a natural-language question. Submitting (button click or Enter) sends the question to the retrieval → generation pipeline. Four example questions are provided as one-click prompts.

**Output fields:**
- **Answer** — a read-only textbox containing the grounded answer with inline "According to [source]:" citations.
- **Retrieved Sources** — a Markdown panel listing each retrieved chunk's source document and its cosine-distance relevance score, so the user can verify which documents the answer was built from.

**Sample interaction transcript:**

```
[User types in "Your Question"]
> How affordable is this college according to student reviews?

[Answer]
According to [Document 1 - niche_sample]: The college is "expensive" and
"Financial aid varies widely."
According to [Document 7 - reddit_reviews]: The college is "Expensive" and
"financial aid wasn't generous."
Overall, student reviews indicate that the college is not very affordable,
with high costs and varying financial aid.

[Retrieved from:]
• niche_sample (relevance: 0.3440)
• niche_sample (relevance: 0.4032)
• niche_sample (relevance: 0.4671)
• sample_reviews (relevance: 0.4804)
• niche_sample (relevance: 0.4850)
```

---

## Evaluation Report

All five questions were run through the live system (`test_e2e.py`) against the Groq `llama-3.3-70b-versatile` model with top-k=8 retrieval. The "system response" column summarizes the actual generated answer; the "avg distance" is the mean cosine distance of the 8 retrieved chunks (lower = better match).

| #   | Question                                                                         | Expected answer                                                                                                                                   | System response (summarized)                                                                                                                                                                                       | Avg distance | Retrieval quality  | Response accuracy  |
| --- | -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------ | ------------------ | ------------------ |
| 1   | What do students say about professor quality and workload at Allegheny?          | Mix of responses covering professor accessibility, grading fairness, homework volume; specific examples from Rate My Professors or Reddit threads | Cited `sample_reviews`, `niche_sample`, `reddit_reviews`: Prof. Miller is engaging with fair grading and 3–4 hrs/week CS homework; the intro biology professor has poor delivery and tests untaught material; professors generally care; workload is "heavy but manageable." | 0.5129       | Relevant           | Accurate           |
| 2   | What are the main complaints about campus life and social environment?           | References to dorm quality, dining, social scene accessibility, inclusivity issues across multiple source perspectives                            | Cited `niche_sample`, `sample_reviews`, `reddit_reviews`: frustrating housing lottery, mediocre dining, cliquey/effort-required social scene, near-impossible parking, poorly lit areas near the old science building, surrounding property crime, small freshman dorms.       | 0.4737       | Relevant           | Accurate           |
| 3   | How affordable is this college according to student reviews?                     | Financial aid experiences, hidden costs, part-time job necessity; sourced from Best Colleges affordability data + student forum discussions       | Cited `niche_sample`, `reddit_reviews`: college is "expensive," financial aid "varies widely" and "wasn't generous," cost is high relative to peers and significant out-of-state. Concludes it is "not very affordable."                                                       | 0.4609       | Relevant           | Accurate           |
| 4   | What do students say about internship and career support?                        | Post-graduation outcomes, recruiting presence, career services quality mentioned in College Confidential or Reddit discussions                    | Cited `sample_reviews`, `reddit_reviews`: career services "helpful but understaffed," internship recruiting "strong in finance and tech, weaker in humanities," and "excellent internship opportunities with major tech companies." Thin on humanities/placement detail.       | 0.6070       | Partially relevant | Partially accurate |
| 5   | Compare student satisfaction: how does this school rank among peer institutions? | Comparative sentiment across Niche ratings, Best Colleges rankings, and peer school discussions                                                   | Cited `niche_sample`, `best_colleges`: 4.2/5 overall satisfaction with strong academics, beautiful/safe campus, strong community; high cost. Then explicitly states it lacks enough information to compare against peer institutions.                                          | 0.5348       | Partially relevant | Partially accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

**Summary:** 3/5 queries (Q1–Q3) returned highly accurate, well-grounded answers with avg distances at or below ~0.51. Q4 and Q5 are partially accurate. Q4 has the worst retrieval (avg 0.6070) — the corpus simply contains little detail on humanities outcomes or placement rates, so the model returned a thin answer. Q5 is honest about its limits: it summarizes satisfaction scores but explicitly declines to invent a peer-institution comparison the documents don't support. This refusal is the *correct* behavior even though it makes the answer "partially" responsive to the literal question.

---

## Failure Case Analysis

**Question that failed:** Q4: "What do students say about internship and career support?"

**What the system returned:** The model answered that career services is "helpful but understaffed," that internship recruiting is "strong in finance and tech, weaker in humanities," and that there are "excellent internship opportunities with major tech companies." It is grounded and not hallucinated, but it is thin: it repeats the same two `sample_reviews` sentences (one of them cited twice as "Document 1" and "Document 7"), gives no concrete placement rates, salary data, or humanities outcomes, and reads as partially responsive rather than thorough.

**Root cause (tied to a specific pipeline stage):** **Retrieval — semantic mismatch and sparse coverage.** This query had the worst retrieval of all five questions: an average cosine distance of **0.6070** across the top-8 chunks, versus 0.46–0.53 for the other four. Two things compound here:
1. *Vocabulary gap at the embedding stage.* The query uses "internship" and "career support," but the documents that actually discuss outcomes phrase it as "recruiting," "placement," "grad school," and "got a job." `all-MiniLM-L6-v2` doesn't bridge that gap tightly, so genuinely relevant chunks (e.g., the `reddit_2` post that says Allegheny is "great for getting into grad school and less so for getting a job") rank lower and the top results drift toward generic career-services mentions.
2. *Sparse coverage in the corpus.* The documents contain only a couple of sentences about career outcomes, so even perfect retrieval would surface limited material. With nothing richer to ground on, the model can only restate what little exists, which is why the same sentence appears twice.

**What you would change to fix it:**
1. **Augment source documents** with detailed career-outcome data (placement rates by major, starting salaries, alumni testimonials about the job search) so retrieval has substantive material to return.
2. **Add query expansion** — when a user asks about "internship support," also embed and search related terms ("recruiting," "placement," "alumni network," "grad school outcomes") and merge the results, directly attacking the vocabulary gap that pushed distance to 0.6070.
3. **Deduplicate retrieved chunks before prompting** so the same sentence can't be cited twice and crowd out a more diverse chunk, and consider raising top-k for high-distance queries to widen context.

---

## Spec Reflection

**One way the spec helped you during implementation:**

The **Chunking Strategy section** in planning.md was invaluable. By specifying chunk size (300 chars), overlap (50 chars), and reasoning *before* coding, I avoided the common RAG mistake of guessing at these values. When testing retrieval, I could trace poor results directly back to the spec and validate that the implementation matched it. The spec forced me to think about the trade-off between chunk size and retrieval precision upfront — small chunks risk fragmenting reviews, large chunks dilute specificity. Having this decision documented meant I could focus on debugging retrieval quality rather than second-guessing architectural choices.

**One way your implementation diverged from the spec, and why:**

The **generation provider** diverged from the plan. The Architecture diagram in planning.md labels the generation stage "Claude API + system prompt for grounding," but the shipped implementation (`generation.py`) calls **Groq's `llama-3.3-70b-versatile`** instead. I switched because Groq offers a free API key with no credit card and very low latency, which removed a cost/setup barrier during development; the grounding system prompt is model-agnostic, so the swap required no change to the grounding design itself — only to the client and the message format (Groq's `chat.completions` API takes the system instruction as a `system`-role message in the `messages` array rather than a separate `system=` parameter). A second, smaller divergence: planning.md mentioned ChromaDB but didn't specify storage mode, and I chose **persistent on-disk** storage so embeddings could be reused across runs rather than re-embedded every session.

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

---

## Stretch Features

### Metadata Filtering

The vector store keeps each chunk's `source` document name in its ChromaDB metadata, so retrieval can be restricted to specific sources. `ChunksEmbedder.retrieve()` accepts a `where` filter, `GroundedGenerator` exposes `available_sources()` and a `source_filter` argument, and the Gradio UI adds a **"Filter by source (optional)"** multi-select dropdown. When one or more sources are selected, ChromaDB applies `{"source": value}` (or `{"source": {"$in": [...]}}` for multiple) so only chunks from those documents are eligible for retrieval.

**Visible effect** — same query (`"What do students say about professor quality and workload?"`, top-5):

| Filter | Returned sources (distance) |
| ------ | --------------------------- |
| *None (all docs)* | sample_reviews (0.3976), sample_reviews (0.4387), niche_sample (0.5069), niche_sample (0.5091), reddit_reviews (0.5411) |
| `source = rate_my_professors` | rate_my_professors (0.5918), rate_my_professors (0.6101), rate_my_professors (0.7027) |
| `source ∈ {reddit, reddit_2}` | reddit_2 (0.7558), reddit (0.8050), reddit_2 (0.8474), reddit (0.8747), reddit_2 (0.9574) |

The filter demonstrably changes which chunks are returned: the unfiltered query pulls the best matches from `sample_reviews`/`niche_sample`, while filtering to `rate_my_professors` returns only that source's three chunks (and the metadata constraint caps the result set at the number of matching chunks, which is why fewer than 5 come back). The higher distances under filtering also show the trade-off — forcing a single source can exclude the globally best matches.

### Chunking Strategy Comparison

`chunking_comparison.py` rebuilds the full corpus under three (chunk size / overlap) settings, embeds each with `all-MiniLM-L6-v2` into an in-memory ChromaDB collection, and runs the same three evaluation queries against each. Lower average cosine distance over the top-8 results = tighter retrieval.

| Strategy (size/overlap) | # chunks | Q1 (professors) | Q2 (campus life) | Q3 (affordability) | Overall avg |
| ----------------------- | -------- | --------------- | ---------------- | ------------------ | ----------- |
| 150 / 30 (fine)         | 127      | 0.5038          | 0.4475           | 0.4597             | **0.4703**  |
| 300 / 50 (production)   | 64       | 0.5129          | 0.4737           | 0.4609             | 0.4825      |
| 600 / 100 (coarse)      | 35       | 0.5249          | 0.4537           | 0.4490             | 0.4759      |

**Which performed better, and why:** On raw retrieval distance the **150/30 fine-grained** strategy wins overall (0.4703) and produces the single best hit of the entire experiment (0.2688 on affordability). This makes sense for this corpus: the documents are short, opinion-dense reviews, so smaller chunks isolate a single sentiment (e.g., just the "expensive / financial aid varies" line) and match a focused query very tightly, with less unrelated text to dilute the embedding. The 600/100 coarse strategy is a close second on the broader Q2/Q3 queries because each large chunk packs more on-topic context, but it loses on the specific professor query (Q1, 0.5249) where extra text adds noise. The **300/50 production setting actually had the highest average distance** of the three.

So why keep 300/50? Distance isn't the only objective — **generation quality** matters too. The 150/30 chunks frequently sever a review mid-thought (e.g., splitting "engaging professor **but** harsh grader" across two chunks), which produces tighter retrieval scores but worse, fragmented context for the LLM to ground on. 300/50 is the deliberate compromise: distances within ~0.01–0.02 of the best while preserving complete review statements. The comparison confirms the chunk size could be tuned down if pure retrieval distance were the goal, but validates 300/50 as the right balance for grounded *generation*.
