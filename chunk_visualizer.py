import gradio as gr
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import os
from dotenv import load_dotenv

load_dotenv()

# 기본 PDF 경로 (LlamaParse로 md 생성시 사용)
PDF_PATH = "data/gemini-2.5-tech_1-2.pdf"

# 기본 MD 경로(없으면 LlamaParse 시도)
DEFAULT_PARSED_MD_PATH = "llamaparse_output_gemini_3.md"

# 1) Markdown 로더
def get_text_from_markdown(file_path: str):
    """지정된 markdown 경로를 읽고, 없으면 LlamaParse로 생성 시도"""
    if not file_path:
        return "Error: markdown 파일 경로가 비어있습니다."

    if not os.path.exists(file_path):
        print(f"'{file_path}' not found. Attempting to parse PDF with LlamaParse...")
        api_key = os.getenv("LLAMA_CLOUD_API_KEY")
        if not api_key:
            return "Error: LLAMA_CLOUD_API_KEY not found. Please set it in your .env file."
        try:
            from llama_parse import LlamaParse
            parser = LlamaParse(result_type="markdown", api_key=api_key)
            documents = parser.load_data(PDF_PATH)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join([doc.text for doc in documents]))
            print(f"Successfully parsed PDF and saved to '{file_path}'")
        except Exception as e:
            return f"LlamaParse processing error: {e}"

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except Exception as e:
        return f"An error occurred while reading the file: {e}"

# 2) 비주얼라이즈 함수
def visualize_splitting(
    md_file,                 # gr.File (업로드된 파일 객체 또는 None)
    md_path_text,            # gr.Textbox (문자열 경로)
    parent_chunk_size,
    parent_chunk_overlap,
    child_chunk_size,
    child_chunk_overlap
):
    """
    업로드된 파일이 있으면 그 경로를 우선 사용.
    없으면 텍스트로 입력한 경로를 사용.
    """
    # 업로더 우선, 없으면 텍스트 경로, 둘 다 없으면 기본값
    resolved_path = None
    if md_file is not None:
        # gr.File 객체는 {'name': 경로, 'orig_name': 원래파일명} 형태일 수 있음
        # gradio 버전에 따라 md_file이 str일 수도 있으므로 안전 처리
        if isinstance(md_file, dict) and "name" in md_file:
            resolved_path = md_file["name"]
        elif hasattr(md_file, "name"):
            resolved_path = md_file.name
        elif isinstance(md_file, str):
            resolved_path = md_file
    if not resolved_path:
        resolved_path = md_path_text.strip() if md_path_text else DEFAULT_PARSED_MD_PATH

    # 숫자형 캐스팅 (Gradio Number가 float로 전달될 수 있음)
    try:
        parent_chunk_size = int(parent_chunk_size)
        parent_chunk_overlap = int(parent_chunk_overlap)
        child_chunk_size = int(child_chunk_size)
        child_chunk_overlap = int(child_chunk_overlap)
    except Exception:
        return "Error: 청크 설정 값이 숫자가 아닙니다. 정수로 입력해 주세요."

    # 텍스트 로드
    source_text = get_text_from_markdown(resolved_path)
    if isinstance(source_text, str) and source_text.startswith(("Error:", "LlamaParse processing error:", "An error occurred")):
        return source_text

    # 스플리터 생성
    parent_splitter = RecursiveCharacterTextSplitter(
        chunk_size=parent_chunk_size,
        chunk_overlap=parent_chunk_overlap
    )
    child_splitter = RecursiveCharacterTextSplitter(
        chunk_size=child_chunk_size,
        chunk_overlap=child_chunk_overlap
    )

    # 부모 문서 생성
    parent_docs = parent_splitter.create_documents([source_text])

    # 결과 마크다운
    markdown_output = [f"# Chunk Visualization Result for `{resolved_path}`"]

    if not parent_docs:
        markdown_output.append("No parent chunks were created. Try adjusting the chunk size.")
        return "\n".join(markdown_output)

    for i, doc in enumerate(parent_docs):
        markdown_output.append(f"\n---\n## Parent Chunk {i + 1}\n")
        markdown_output.append(f"**Size:** {len(doc.page_content)} characters")
        markdown_output.append("```")
        markdown_output.append(doc.page_content)
        markdown_output.append("```")

        # 자식 청크
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

# 3) Gradio UI
with gr.Blocks(theme="soft", css="h1, h2, h3, h4 {font-weight: bold;}") as demo:
    gr.Markdown(f"# LangChain Text Splitter Visualizer")
    gr.Markdown(
        "아래에서 **Markdown 파일 경로**를 입력하시거나 **.md 파일을 업로드**하시면, "
        "`RecursiveCharacterTextSplitter`의 부모/자식 청크 분할 결과를 시각화합니다. "
        "업로드가 있을 경우 업로드 파일이 **우선** 사용됩니다."
    )

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Markdown 파일 선택")
            md_file = gr.File(label="업로드(.md)", file_types=[".md"], type="filepath")
            md_path_text = gr.Textbox(
                label="Markdown 파일 경로(업로드 없을 때 사용)",
                value=DEFAULT_PARSED_MD_PATH,
                placeholder="예) ./llamaparse_output_gemini_3.md"
            )
        with gr.Column(scale=1):
            gr.Markdown("### Parent Splitter Settings")
            p_chunk_size = gr.Number(label="Chunk Size", value=2000)
            p_chunk_overlap = gr.Number(label="Chunk Overlap", value=200)

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Child Splitter Settings")
            c_chunk_size = gr.Number(label="Chunk Size", value=400)
            c_chunk_overlap = gr.Number(label="Chunk Overlap", value=40)

    process_btn = gr.Button("Run Splitter Visualization", variant="primary")
    output_display = gr.Markdown(label="Visualization Output")

    process_btn.click(
        fn=visualize_splitting,
        inputs=[md_file, md_path_text, p_chunk_size, p_chunk_overlap, c_chunk_size, c_chunk_overlap],
        outputs=[output_display]
    )

# LAN 공유는 server_name, 외부 공유는 share 사용
demo.launch(server_port=7880, share=True)
