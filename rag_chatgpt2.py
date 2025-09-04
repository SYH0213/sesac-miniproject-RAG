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

# ===================== 기본 설정 =====================
load_dotenv()

# 대화 메모리 (메시지 리스트 반환)
memory = ConversationBufferMemory(return_messages=True)

# LLM (헛소리/외부지식 최소화를 위해 temperature=0 권장)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 파일 경로
PDF_PATH = "data/gemini-2.5-tech_1-2.pdf"
PARSED_MD_PATH = "llamaparse_output_gemini_1_2.md"
CHROMA_DB_DIR = "./chroma_db"

# ===================== RAG 구성 =====================
# 1) 스플리터
parent_splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=300)
child_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

# 2) 임베딩 + 벡터스토어
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=embeddings)

# 3) ParentDocumentRetriever
store = InMemoryStore()
retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=store,
    child_splitter=child_splitter,
    parent_splitter=parent_splitter,
)

# ===================== 문서 적재/색인 =====================
def load_and_populate_vectorstore():
    try:
        # 이미 색인되어 있으면 스킵
        if hasattr(vectorstore, "_collection") and vectorstore._collection.count() > 0:
            print("Vector store already populated. Skipping document loading.")
            return
    except Exception:
        pass  # 버전 차이 대비

    # 파싱된 마크다운 없으면 LlamaParse 수행
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
    
    # 마크다운 로드 후 색인
    print(f"Loading document from '{PARSED_MD_PATH}'...")
    try:
        with open(PARSED_MD_PATH, "r", encoding="utf-8") as f:
            text = f.read()
        docs = [Document(page_content=text)]
        print("Adding documents to vector store...")
        retriever.add_documents(docs)
        try:
            print(f"Vector store populated with {vectorstore._collection.count()} documents.")
        except Exception:
            print("Vector store populated.")
    except Exception as e:
        print(f"Error loading or processing markdown file: {e}")

# ===================== 체인 구성 =====================
# (1) 히스토리 인지형 리트리버용 프롬프트
contextualize_q_system_prompt = (
    "Given a chat history and the latest user question which might reference context in the chat history, "
    "formulate a standalone question which can be understood without the chat history. "
    "Do NOT answer the question, just reformulate it if needed and otherwise return it as is."
)
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ]
)

# (2) 히스토리 인지형 리트리버 생성
history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt
)

# (3) 최종 답변 프롬프트 (context는 문자열로 주입)
ga_system_prompt = (
    "You are an assistant for question-answering tasks. "
    "Answer ONLY with information from the provided context. "
    "If you don't know the answer, say you don't know. "
    "Use up to three sentences. Be concise."
)
ga_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", ga_system_prompt + "\n\n[Context]\n{context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ]
)

# (4) 문서 결합 체인 + RAG 체인
question_answer_chain = create_stuff_documents_chain(llm, ga_prompt)
rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

# ===================== 질의 함수 =====================
def ask_llm(query: str, history: list):
    # 메모리에서 대화 이력 로드
    chat_history = memory.load_memory_variables({}).get("history", [])

    try:
        response = rag_chain.invoke({"input": query, "chat_history": chat_history})
        answer = response.get("answer", "")

        # 외부로 보여줄 컨텍스트(사이드 패널)
        retrieved = response.get("context", None)
        context_text = "## 참조 문서\n\n"
        if isinstance(retrieved, list) and len(retrieved) > 0:
            for i, doc in enumerate(retrieved):
                content = getattr(doc, "page_content", str(doc))
                context_text += f"### 문서 {i+1}\n```\n{content}\n```\n\n"
        elif isinstance(retrieved, str) and retrieved.strip():
            context_text += f"```\n{retrieved}\n```\n"
        else:
            context_text += "참조된 문서가 없습니다."

        # 메모리에 현재 질의/응답 저장
        memory.save_context({"input": query}, {"output": answer})

        # ChatInterface 규약: 첫 번째는 어시스턴트 메시지(문자열), 그 뒤로 additional_outputs
        return answer, context_text

    except Exception as e:
        err = f"오류 발생: {e}"
        # ❗예외 시에도 첫 번째 리턴은 반드시 문자열로!
        fallback_context = "## 참조 문서\n\n(에러로 인해 컨텍스트 표시 불가)\n"
        return err, fallback_context

# ===================== UI =====================
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
            # 사이드 패널로 보여줄 컨텍스트 컴포넌트(추가 출력 바인딩)
            context_display = gr.Markdown(label="LLM 참조 문서 전문")

            chat = gr.ChatInterface(
                fn=ask_llm,
                chatbot=gr.Chatbot(height=400, type="messages"),
                additional_outputs=[context_display],
                examples=example_questions_doc_content + example_questions_excel,
                cache_examples=False,
                theme="soft"
            )
            chat.render()

            with gr.Accordion("예시 질문 카테고리 보기", open=False):
                gr.Markdown("### 문서 내용 확인용")
                gr.Markdown("\n".join(f"- {q}" for q in example_questions_doc_content))
                gr.Markdown("### 엑셀표 로드 확인용")
                gr.Markdown("\n".join(f"- {q}" for q in example_questions_excel))

        with gr.Column(scale=1):
            gr.Markdown("## LLM 참조 문서 전문")
            # 위의 context_display와 동일 객체이므로 여기서 그대로 보여짐
            # (추가로 아무 것도 필요 없음)

demo.launch()
