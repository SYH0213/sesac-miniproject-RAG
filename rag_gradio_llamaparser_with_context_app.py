import gradio as gr
from openai import OpenAI
import os
from dotenv import load_dotenv
from llama_parse import LlamaParse

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain.schema import Document
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

# 환경변수 로드
load_dotenv()

# LLM 모델 초기화
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# --- Document Loading and Caching ---
PDF_PATH = "data/gemini-2.5-tech_1-2.pdf"
PARSED_MD_PATH = "llamaparse_output_gemini_1_2.md"
CHROMA_DB_DIR = "./chroma_db"

# --- RAG Setup ---

# 1. Text Splitters
parent_splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=300)
child_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

# 2. Embedding Model
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# 3. Vector Store (ChromaDB)
vectorstore = Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=embeddings)

# 4. ParentDocumentRetriever
store = InMemoryStore()
retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=store,
    child_splitter=child_splitter,
    parent_splitter=parent_splitter,
)

# --- Data Loading and Vector Store Population ---
def load_and_populate_vectorstore():
    # Step 1: Check if the vector store is already populated.
    if vectorstore._collection.count() > 0:
        print(f"Vector store already populated with {vectorstore._collection.count()} documents. Skipping.")
        return

    # Step 2: If not populated, check for the parsed markdown file.
    if not os.path.exists(PARSED_MD_PATH):
        print(f"'{PARSED_MD_PATH}' not found. Processing PDF with LlamaParse...")
        api_key = os.getenv("LLAMA_CLOUD_API_KEY")
        if not api_key:
            print("Error: LLAMA_CLOUD_API_KEY not found.")
            return
        try:
            parser = LlamaParse(result_type="markdown", api_key=api_key)
            documents = parser.load_data(PDF_PATH)
            with open(PARSED_MD_PATH, "w", encoding="utf-8") as f:
                f.write("\n".join([doc.text for doc in documents]))
            print(f"Successfully parsed and saved to '{PARSED_MD_PATH}'")
        except Exception as e:
            print(f"LlamaParse processing error: {e}")
            return
    
    # Step 3: Load the document and add to the vector store.
    print(f"Loading document from '{PARSED_MD_PATH}'...")
    try:
        with open(PARSED_MD_PATH, "r", encoding="utf-8") as f:
            text = f.read()
        documents = [Document(page_content=text)]
        print("Adding documents to vector store...")
        retriever.add_documents(documents)
        print(f"Vector store populated with {vectorstore._collection.count()} documents.")
    except Exception as e:
        print(f"Error loading or processing markdown file: {e}")

# --- Conversational RAG Chain Setup ---

# 1. Prompt for History-Aware Retriever
contextualize_q_system_prompt = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, "
    "just reformulate it if needed and otherwise return it as is."
)
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ]
)

# 2. Create the History-Aware Retriever
history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt
)

# 3. Prompt for Final Answer Generation
ga_system_prompt = (
    "You are a helpful assistant. Your ONLY task is to answer the user's question STRICTLY based on the provided context. "
    "If the information to answer the question is present in the context, provide a concise answer. "
    "If the answer cannot be found within the provided context, you MUST say '제공된 문서의 내용으로는 답변할 수 없습니다.' Do NOT use any of your outside knowledge."
    "\n\nContext:\n{context}"
)
ga_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", ga_system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ]
)

# 4. Create the Document Chain
question_answer_chain = create_stuff_documents_chain(llm, ga_prompt)

# --- RAG Function ---
def ask_llm(query, history):
    chat_history_for_chain = []
    if history:
        for message in history:
            if message["role"] == "user":
                chat_history_for_chain.append(HumanMessage(content=message["content"]))
            elif message["role"] == "assistant":
                chat_history_for_chain.append(AIMessage(content=message["content"]))

    try:
        # --- DEBUGGING STARTS HERE ---
        print("\n" + "="*50)
        print(f"DEBUG: Current Query: {query}")
        
        print("\n--- 1. Invoking History-Aware Retriever to get documents ---")
        retrieved_docs = history_aware_retriever.invoke({
            "input": query,
            "chat_history": chat_history_for_chain
        })
        print(f"\n--- 2. Retriever found {len(retrieved_docs)} documents. ---")
        if retrieved_docs:
            for i, doc in enumerate(retrieved_docs):
                source = doc.metadata.get('source', 'N/A') if hasattr(doc, 'metadata') else 'N/A'
                print(f"--- Document {i+1} (Source: {source}) ---")
                print(doc.page_content[:300] + "...")
                print("-"*(len(f"--- Document {i+1} (Source: {source}) ---")))
        print("\n" + "="*50)

        print("\n--- 3. Invoking Document Chain to generate answer ---")
        final_input = {
            "input": query,
            "chat_history": chat_history_for_chain,
            "context": retrieved_docs
        }
        answer = question_answer_chain.invoke(final_input)
        print(f"\n--- 4. Final Answer Generated ---")
        print(answer)
        print("="*50 + "\n")
        # --- DEBUGGING ENDS HERE ---

        context_text = "## 참조 문서\n\n"
        if retrieved_docs:
            for i, doc in enumerate(retrieved_docs):
                context_text += f"### 문서 {i+1}\n"
                context_text += f"```\n{doc.page_content}\n```\n\n"
        else:
            context_text += "참조된 문서가 없습니다."

        if not history:
            history = []
        history.append({"role": "user", "content": query})
        history.append({"role": "assistant", "content": answer})
        
        return "", history, context_text
        
    except Exception as e:
        error_message = f"오류 발생: {e}"
        debug_info = f"\n\nDEBUG INFO:\nQuery: {query}\nHistory: {history}"
        full_error = f"{error_message}{debug_info}"
        print(f"ERROR in ask_llm: {full_error}")

        if not history:
            history = []
        history.append({"role": "user", "content": query})
        history.append({"role": "assistant", "content": error_message})
        return "", history, "참조된 문서가 없습니다."

# --- Vector Store Management Function ---
def force_reload_vectorstore():
    print("---" + " Forcing reload of vector store ---")
    try:
        print("Attempting to reset the collection via chromadb client...")
        vectorstore._client.reset()
        print("Successfully reset the chromadb client.")
        
        load_and_populate_vectorstore()
        return "✅ Vector store reloaded successfully!"
    except Exception as e:
        error_msg = f"❌ Error during vector store reload: {e}"
        print(error_msg)
        return error_msg

# --- Gradio Interface ---
load_and_populate_vectorstore()

example_questions_doc_content = [
    "Gemini 2.5는 어떤 모델 계열로 설명되고 있나요?",
    "문서에서 강조하는 Gemini 2.5의 주요 특징은 무엇인가요?",
    "Gemini 2.5의 성능이 어떤 평가 지표를 기준으로 설명되고 있나요?",
    "Gemini 2.5 모델 크기나 변형(variants)에 대한 언급이 있나요?",
    "Gemini 2.5는 어떤 방식으로 기존 모델 대비 개선되었다고 하나요?"
]

example_questions_excel = [
    "엑셀(표)에서 Gemini 2.5와 다른 모델들의 성능 비교 결과는 어떻게 나오나요?",
    "표에 따르면 Gemini 2.5가 수학/코딩 분야에서 어떤 성능을 보이나요?",
    "엑셀표에 MMLU 점수가 기재되어 있나요? 있다면 Gemini 2.5의 점수는 얼마인가요?",
    "표에서 경쟁 모델과 Gemini 2.5의 차이가 가장 크게 나타나는 분야는 어디인가요?",
    "엑셀표 형식 데이터가 잘 불러와졌는지 확인하기 위해, 문서 내 첫 번째 표의 항목 이름을 나열해줄래요?"
]

with gr.Blocks(theme="soft", title="PDF RAG Chatbot") as demo:
    gr.Markdown("# PDF RAG Chatbot (LlamaParse + Conversational)")
    gr.Markdown("PDF 문서 내용에 대해 질문하세요. (대화 내용 기억 기능 포함)")
    
    with gr.Row():
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(height=400, label="Chat", type='messages', value=[])
            msg = gr.Textbox(label="질문을 입력하세요...")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 문서 내용 확인용")
                    gr.Examples(
                        examples=example_questions_doc_content,
                        inputs=msg,
                        label="문서 내용 확인용 질문"
                    )
                with gr.Column():
                    gr.Markdown("### 엑셀표 로드 확인용")
                    gr.Examples(
                        examples=example_questions_excel,
                        inputs=msg,
                        label="엑셀표 로드 확인용 질문"
                    )
        with gr.Column(scale=1):
            context_display = gr.Markdown(label="LLM 참조 문서 전문")
            with gr.Accordion("⚙️ Advanced Options", open=False):
                reload_button = gr.Button("🔄 Force Reload Vector Store")
                reload_status = gr.Markdown()

    clear = gr.ClearButton([msg, chatbot, context_display])
    msg.submit(ask_llm, [msg, chatbot], [msg, chatbot, context_display])
    reload_button.click(force_reload_vectorstore, outputs=reload_status)

demo.launch()