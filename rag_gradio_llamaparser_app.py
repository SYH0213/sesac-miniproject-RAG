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
llm = ChatOpenAI(model="gpt-4o-mini")

# --- Document Loading and Caching ---
PDF_PATH = "data/gemini-2.5-tech_1-10.pdf"
PARSED_MD_PATH = "llamaparse_output_full.md"
CHROMA_DB_DIR = "./chroma_db"

# --- RAG Setup ---

# 1. Text Splitters
parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
child_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=40)

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

# --- Process PDF via LlamaParse and Populate Vector Store ---
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
    "You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question.     "If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.\n"    Question: {input}\n"    Context: {context}\n"    Answer:"
)
ga_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", ga_system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="context"),
    ]
)

# 4. Create the Document Chain
question_answer_chain = create_stuff_documents_chain(llm, ga_prompt)

# 5. Create the full RAG chain
rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)


# --- RAG Function ---
def ask_llm(query, history):
    # Convert Gradio history format to LangChain format
    chat_history = []
    for message_dict in history:
        role = message_dict.get('role')
        content = message_dict.get('content')
        if role == 'user':
            chat_history.append(HumanMessage(content=content))
        elif role == 'assistant':
            chat_history.append(AIMessage(content=content))

    # Invoke the RAG chain
    try:
        response = rag_chain.invoke({"input": query, "chat_history": chat_history})
        return response["answer"]
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

    gr.Examples(
        examples=example_questions,
        inputs=[gr.Textbox(label="질문 입력")],
        label="예시 질문"
    )

demo.launch()
