import gradio as gr
import fitz  # PyMuPDF
from openai import OpenAI
import os
from dotenv import load_dotenv
import shutil

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain.schema import Document

# 환경변수 로드
load_dotenv()
# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# --- PDF Loading and Text Extraction ---
pdf_path = "data/gemini-2.5-tech_1-10.pdf"  # Updated PDF path

# Directory for ChromaDB persistence
CHROMA_DB_DIR = "./chroma_db"

# --- RAG Setup ---

# 1. Text Splitters
parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
child_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=40)

# 2. Embedding Model
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# 3. Vector Store (ChromaDB) and Caching
vectorstore = Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=embeddings)

# 4. ParentDocumentRetriever
store = InMemoryStore()
retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=store,
    child_splitter=child_splitter,
    parent_splitter=parent_splitter,
)

# --- Process PDF and Populate Vector Store (if not already populated) ---
def process_pdf_and_populate_vectorstore(pdf_file_path):
    print("Processing PDF and populating vector store with PyMuPDF...")
    documents = []
    try:
        with fitz.open(pdf_file_path) as doc:  # Use fitz.open
            for i, page in enumerate(doc):
                text = page.get_text("text")  # Use get_text("text")
                if text:
                    documents.append(Document(page_content=text, metadata={"page": i + 1}))
    except Exception as e:
        print(f"Error loading PDF: {e}")
        return

    # Add documents to the retriever
    if vectorstore._collection.count() == 0:
        print("Vector store is empty. Adding documents...")
        retriever.add_documents(documents)
        print(f"Vector store populated with {vectorstore._collection.count()} documents.")
    else:
        print("Vector store already populated. Skipping document addition.")

# Call the function to process PDF and populate vector store on startup
process_pdf_and_populate_vectorstore(pdf_path)

# --- RAG Function ---
def ask_llm(query, history):
    global vectorstore, retriever
    
    retrieved_docs = retriever.invoke(query)
    
    print(f"\n--- Retrieved Documents ({len(retrieved_docs)}): ---")
    for i, doc in enumerate(retrieved_docs):
        print(f"Document {i+1} (Page {doc.metadata.get('page', 'N/A')}):")
        print(doc.page_content[:200] + "...")
        print("--------------------------------------------------")

    if len(retrieved_docs) == 0 and vectorstore._collection.count() > 0:
        print("\n--- WARNING: No documents retrieved. Resetting collection. ---")
        vectorstore.delete_collection()
        print("Deleted ChromaDB collection.")
        
        vectorstore = Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=embeddings)
        store = InMemoryStore()
        retriever = ParentDocumentRetriever(
            vectorstore=vectorstore,
            docstore=store,
            child_splitter=child_splitter,
            parent_splitter=parent_splitter,
        )
        process_pdf_and_populate_vectorstore(pdf_path)
        
        retrieved_docs = retriever.invoke(query)
        print(f"\n--- Retrieved Documents after re-population ({len(retrieved_docs)}): ---")
        if len(retrieved_docs) == 0:
            return "벡터 저장소 재구축 후에도 관련 문서를 찾을 수 없습니다."
        else:
            return "벡터 저장소에 문제가 감지되어 재구축했습니다. 질문을 다시 시도해 주세요."

    context_text = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])
    
    context = f"""You are an AI assistant. Answer the user's question based on the following document content. If the answer is not in the document, state that you don't know. Answer in Korean.

Document Content:
{context_text}

User Question: {query}"""

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": context,
                }
            ],
            model="gpt-4o-mini",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error communicating with LLM: {e}"

# --- Gradio Interface ---
example_questions = ["Gemini 2.5는 무엇인가요?", "주요 기능은 무엇인가요?", "이 문서에 어떤 내용이 있나요?"]

with gr.Blocks(theme="soft", title="PDF RAG Chatbot") as demo:
    gr.Markdown("# PDF RAG Chatbot (고급 RAG)")
    gr.Markdown("PDF 문서 내용에 대해 질문하세요. (청킹, 임베딩, 벡터스토어 적용)")
    
    gr.ChatInterface(
        fn=ask_llm,
        chatbot=gr.Chatbot(height=400, type='messages'),
        theme="soft"
    ).render()

    gr.Examples(
        examples=example_questions,
        inputs=[gr.Textbox(label="질문 입력")],
        label="예시 질문"
    )

demo.launch()
