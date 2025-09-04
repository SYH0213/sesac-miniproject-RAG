import gradio as gr
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import re

# 1. Function to read and parse the markdown file
def get_text_from_markdown(file_path="pymupdf_test_output.md"):
    """Reads the markdown file and extracts text from the code blocks."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Use regex to find all text within ```text ... ``` blocks
        text_blocks = re.findall(r"```text\n(.*?)\n```", content, re.DOTALL)
        full_text = "\n".join(text_blocks)
        return full_text
    except FileNotFoundError:
        return "Error: pymupdf_test_output.md not found. Please run the test_pymupdf.py script first."
    except Exception as e:
        return f"An error occurred while reading the file: {e}"

# 2. Main function to split the text and visualize
def visualize_splitting(parent_chunk_size, parent_chunk_overlap, child_chunk_size, child_chunk_overlap):
    """
    Loads text, splits it into parent and child chunks,
    and returns a markdown visualization.
    """
    # Load the text
    source_text = get_text_from_markdown()
    if source_text.startswith("Error:"):
        return source_text

    # Initialize splitters
    parent_splitter = RecursiveCharacterTextSplitter(
        chunk_size=parent_chunk_size,
        chunk_overlap=parent_chunk_overlap
    )
    child_splitter = RecursiveCharacterTextSplitter(
        chunk_size=child_chunk_size,
        chunk_overlap=child_chunk_overlap
    )

    # Create parent documents
    parent_docs = parent_splitter.create_documents([source_text])

    # Prepare markdown output
    markdown_output = ["# Chunk Visualization Result"]

    if not parent_docs:
        markdown_output.append("No parent chunks were created. Try adjusting the chunk size.")
        return "\n".join(markdown_output)

    for i, doc in enumerate(parent_docs):
        # Add parent chunk info
        markdown_output.append(f"\n---\n## Parent Chunk {i + 1}\n")
        markdown_output.append(f"**Size:** {len(doc.page_content)} characters")
        markdown_output.append("```")
        markdown_output.append(doc.page_content)
        markdown_output.append("```")

        # Create and add child chunks info
        child_docs = child_splitter.create_documents([doc.page_content])
        if child_docs:
            markdown_output.append(f"\n### Child Chunks for Parent {i + 1}\n")
            for j, child_doc in enumerate(child_docs):
                markdown_output.append(f"#### Child {j + 1}")
                markdown_output.append(f"**Size:** {len(child_doc.page_content)} characters")
                markdown_output.append("```")
                markdown_output.append(child_doc.page_content)
                markdown_output.append("```")
        else:
            markdown_output.append("\n*No child chunks created for this parent.*")


    return "\n".join(markdown_output)

# 3. Gradio Interface
with gr.Blocks(theme="soft", css="h1, h2, h3, h4 {font-weight: bold;}") as demo:
    gr.Markdown("# LangChain Text Splitter Visualizer")
    gr.Markdown(
        "This app visualizes how `RecursiveCharacterTextSplitter` divides text from `pymupdf_test_output.md` "
        "into parent and child chunks based on your settings."
    )

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Parent Splitter Settings")
            p_chunk_size = gr.Number(label="Chunk Size", value=2000)
            p_chunk_overlap = gr.Number(label="Chunk Overlap", value=200)

        with gr.Column(scale=1):
            gr.Markdown("### Child Splitter Settings")
            c_chunk_size = gr.Number(label="Chunk Size", value=400)
            c_chunk_overlap = gr.Number(label="Chunk Overlap", value=40)

    process_btn = gr.Button("Run Splitter Visualization", variant="primary")

    output_display = gr.Markdown(label="Visualization Output")

    process_btn.click(
        fn=visualize_splitting,
        inputs=[p_chunk_size, p_chunk_overlap, c_chunk_size, c_chunk_overlap],
        outputs=[output_display]
    )

demo.launch()
