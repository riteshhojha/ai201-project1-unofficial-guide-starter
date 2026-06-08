import gradio as gr
from generation import GroundedGenerator


# Initialize generator once
generator = GroundedGenerator()


def answer_question(question: str) -> tuple[str, str]:
    """Handle query and return answer + sources."""
    result = generator.generate(question)

    # Format answer
    answer = result["answer"]

    # Format sources with distance scores
    sources_text = "**Retrieved from:**\n"
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
    submit_btn.click(answer_question, inputs=question, outputs=[answer, sources])
    question.submit(answer_question, inputs=question, outputs=[answer, sources])

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
