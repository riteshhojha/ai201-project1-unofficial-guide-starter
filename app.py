import gradio as gr
from generation import GroundedGenerator


# Initialize generator once
generator = GroundedGenerator()


SOURCE_CHOICES = generator.available_sources()


def answer_question(question: str, source_filter: list) -> tuple[str, str]:
    """Handle query and return answer + sources, optionally filtered by source."""
    result = generator.generate(question, source_filter=source_filter or None)

    # Format answer
    answer = result["answer"]

    # Format sources with distance scores
    if source_filter:
        sources_text = f"**Filtered to:** {', '.join(source_filter)}\n\n"
    else:
        sources_text = ""
    sources_text += "**Retrieved from:**\n"
    for i, chunk in enumerate(result["retrieved_chunks"][:5], 1):
        sources_text += f"• {chunk['source']} (relevance: {chunk['distance']:.4f})\n"

    return answer, sources_text


# Build interface
with gr.Blocks(title="Allegheny College Review System") as demo:
    gr.Markdown("# 🎓 Allegheny College Student Reviews")
    gr.Markdown(
        "Ask questions about student experiences, academics, campus life, and affordability."
    )

    with gr.Row():
        with gr.Column():
            question = gr.Textbox(
                label="Your Question",
                placeholder="e.g., What do students say about professor quality?",
                lines=3,
            )
            source_filter = gr.Dropdown(
                choices=SOURCE_CHOICES,
                value=[],
                multiselect=True,
                label="Filter by source (optional)",
                info="Leave empty to search all documents, or restrict retrieval to specific sources.",
            )
            submit_btn = gr.Button("Ask", size="lg", variant="primary")

        with gr.Column():
            answer = gr.Textbox(
                label="Answer",
                lines=8,
                interactive=False,
            )
            sources = gr.Markdown(
                label="Retrieved Sources",
            )

    # Wire up interactions
    submit_btn.click(
        answer_question, inputs=[question, source_filter], outputs=[answer, sources]
    )
    question.submit(
        answer_question, inputs=[question, source_filter], outputs=[answer, sources]
    )

    gr.Examples(
        examples=[
            ["What do students say about professor quality and workload?"],
            ["How affordable is Allegheny College?"],
            ["What are students' main complaints about campus life?"],
            ["What do students say about internship opportunities?"],
        ],
        inputs=question,
        label="Try these questions:",
    )

    gr.Markdown("""
    ---
    **How this works:** Your question is used to retrieve relevant student reviews from our document database.
    The AI then generates an answer based *only* on the retrieved content, ensuring accuracy and traceability.
    """)


if __name__ == "__main__":
    demo.launch(share=False)
