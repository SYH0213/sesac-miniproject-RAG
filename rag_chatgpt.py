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
from langchain.memory import ConversationBufferMemory

# --- Setup ---
load_dotenv()
memory = ConversationBufferMemory(return_messages=True)
llm = ChatOpenAI(model="gpt-4o-mini")

PDF_PATH = "data/gemini-2.5-tech_1-10.pdf"
PARSED_MD_PATH = "llamaparse_output_full.md"
CHROMA_DB_DIR = "./chroma_db"

# --- RAG Setup ---
parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
child_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=40)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=embeddings)

store = InMemoryStore()
retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=store,
    child_splitter=child_splitter,
    parent_splitter=parent_splitter,
)

def load_and_populate_vectorstore():
    if vectorstore._collection.count() > 0:
        print("Vector store already populated. Skipping document loading.")
        return

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
contextualize_q_system_prompt = (
    "Given a chat history and the latest user question which might reference context "
    "in the chat history, formulate a standalone question.\n"
    "Do NOT answer the question."
)
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ]
)
history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)

# ===== FIXED PART =====
ga_system_prompt = (
    "You are an assistant for question-answering tasks. "
    "Answer the user's question based on the provided context. "
    "If you don't know the answer, say you don't know. "
    "Use three sentences maximum and keep the answer concise.\n\n"
    "Context:\n{context}"
)
ga_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", ga_system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),  # keep as messages
        ("human", "{input}"),
    ]
)
# ======================

question_answer_chain = create_stuff_documents_chain(llm, ga_prompt)
rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

def ask_llm(query, history):
    # history는 Gradio가 주는 대화 이력이지만, 우리는 LangChain 메모리를 사용
    chat_history = memory.load_memory_variables({})["history"]
    try:
        response = rag_chain.invoke({"input": query, "chat_history": chat_history})
        answer = response["answer"]
        memory.save_context({"input": query}, {"output": answer})
        return answer
    except Exception as e:
        return f"An error occurred: {e}"

# --- Gradio Interface ---
load_and_populate_vectorstore()
example_questions = ["Gemini 2.5는 무엇인가요?", "주요 기능은 무엇인가요?", "이 문서에 어떤 내용이 있나요?"]

with gr.Blocks(theme="soft", title="PDF RAG Chatbot") as demo:
    gr.Markdown("# PDF RAG Chatbot (LlamaParse + Conversational)")
    gr.Markdown("PDF 문서 내용에 대해 질문하세요. (대화 내용 기억 기능 포함)")

    gr.ChatInterface(
        fn=ask_llm,
        chatbot=gr.Chatbot(height=400, type='messages'),
        theme="soft"
    ).render()

    # (선택) ChatInterface와 혼용 시 예제 위젯은 제거하거나 별도 입력 컴포넌트로 구성 권장
    # gr.Examples(examples=example_questions, inputs=[gr.Textbox(label="질문 입력")], label="예시 질문")

demo.launch()
