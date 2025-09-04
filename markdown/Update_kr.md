# 업데이트 로그 v1.8

이번 버전은 애플리케이션의 안정성과 사용자 경험을 개선하는 데 중점을 두었습니다. 특히, 반복적으로 발생하던 벡터 스토어의 불안정성 문제를 해결하고, 프롬프트를 강화하여 RAG 시스템의 신뢰도를 높였습니다.

## 핵심 개선 사항

-   **벡터 스토어 '강제 새로고침' 기능 추가 및 안정화:**
    -   간헐적으로 벡터 스토어가 손상되어 문서 검색에 실패하던 문제를 해결하기 위해, UI에 "🔄 Force Reload Vector Store" 버튼을 추가했습니다.
    -   단순히 컬렉션을 삭제하는 방식(`delete_collection`)이 특정 상황에서 실패하던 문제를 해결하기 위해, 더 강력하고 안정적인 내부 `client.reset()` 메소드를 사용하여 데이터베이스를 초기화하도록 로직을 개선했습니다. 이를 통해 사용자는 앱을 재시작하거나 폴더를 직접 삭제할 필요 없이, 버튼 클릭만으로 벡터 스토어를 안정적으로 초기화할 수 있습니다.

-   **프롬프트 강화 (Hallucination 억제):**
    -   챗봇이 제공된 문서에 없는 내용에 대해 답변하는 현상(Hallucination)을 방지하기 위해, 시스템 프롬프트를 대폭 강화했습니다.
    -   "오직 제공된 컨텍스트에만 엄격하게 기반하여 답변"하고, "외부 지식을 절대 사용하지 말 것"을 명시적으로 지시했습니다.
    -   문서에서 답변을 찾을 수 없는 경우, "제공된 문서의 내용으로는 답변할 수 없습니다."라고 정해진 문구를 답변하도록 강제하여, RAG 시스템의 신뢰도를 향상시켰습니다.

-   **디버깅 로그 복원:**
    -   사용자 요청에 따라, 문제 발생 시 원인 파악을 용이하게 하기 위해 RAG 체인의 각 단계(문서 검색, 최종 답변 생성 등)의 결과를 터미널에 출력하는 상세 디버깅 로그를 다시 추가했습니다.

---

# 업데이트 로그 v1.7

## 새로운 기능

-   **컨텍스트 시각화 기능 추가:**
    -   `rag_gradio_llamaparser_with_context_app.py`라는 새로운 Gradio 애플리케이션을 생성하여 고급 UI를 제공합니다.
    -   이 애플리케이션은 채팅 인터페이스를 왼쪽에, LLM이 참조한 문서의 전체 텍스트를 표시하는 전용 패널을 오른쪽에 배치하는 분할 레이아웃을 특징으로 합니다.
    -   `ask_llm` 함수는 채팅 기록과 검색된 컨텍스트를 모두 반환하도록 수정되어, Gradio UI가 컨텍스트 패널을 동적으로 업데이트할 수 있도록 합니다.
    -   `ga_prompt`는 컨텍스트를 메시지 목록으로 올바르게 처리하도록 수정되어, 이전의 `ValueError` 문제를 해결합니다.

---

# 업데이트 로그 v1.6

이번 버전은 사용자 경험 및 RAG 체인의 견고성 향상을 위한 중요한 버그 수정, 메모리 관리 개선 및 UI 개선을 포함합니다.

## 버그 수정

-   **`NameError: name 'qa_prompt' is not defined` 해결:** 최종 답변 생성 프롬프트에서 오타(`qa_prompt`를 `ga_prompt`로 변경)를 수정했습니다.
-   **`ValueError: Prompt must accept context as an input variable` 해결:** 최종 답변 생성 프롬프트(`ga_prompt`)에서 `context`에 대한 `MessagesPlaceholder`의 순서를 재정렬하여 문서 메시지 목록을 올바르게 받도록 했습니다.

## 개선 및 세부 조정

-   **향상된 대화 메모리 통합:**
    -   직접적인 Gradio 기록 구문 분석에서 `langchain.memory.ConversationBufferMemory`를 사용하여 대화 기록을 관리하도록 전환했습니다. 이는 RAG 체인 내에서 대화 컨텍스트를 처리하는 더 견고하고 표준적인 방법을 제공합니다.
    -   `ask_llm` 함수는 이제 `memory`에서 대화 기록을 로드하고 응답 생성 후 현재 상호 작용을 저장합니다.
-   **Gradio UI의 예시 질문 레이아웃 개선:**
    -   Gradio 인터페이스를 재구성하여 예시 질문을 명확한 제목("문서 내용 확인용" 및 "엑셀표 로드 확인용")과 함께 두 개의 개별 열에 표시했습니다.
    -   예시 질문은 이제 메인 채팅 입력과 동적으로 연결되어 사용자가 예시를 클릭하여 입력 필드를 쉽게 채울 수 있습니다.
-   **RAG 체인의 PDF 소스 업데이트:**
    -   RAG 체인의 기본 PDF 문서를 `data/gemini-2.5-tech_1-10.pdf`에서 `data/gemini-2.5-tech_1-2.pdf`로 변경하여 더 작은 데이터 범위에 집중했습니다.
    -   해당 `PARSED_MD_PATH`를 `llamaparse_output_gemini_1_2.md`로 업데이트했습니다.

## 새로운 도구

-   **`chunk_visualizer_for_gemini_pdf.py`:**
    -   `data/gemini-2.5-tech_1-2.pdf`에 대한 텍스트 분할을 시각화하기 위해 새로 생성된 Gradio 애플리케이션입니다.
    -   통합된 LlamaParse 생성 로직을 포함합니다: `llamaparse_output_gemini_1_2.md`가 존재하지 않으면 스크립트는 LlamaParse를 사용하여 `data/gemini-2.5-tech_1-2.pdf`를 자동으로 구문 분석하고 출력을 저장하여 시각화 도구를 자체 포함하도록 합니다.

---

# 업데이트 로그 v1.5

이번 버전은 RAG 애플리케이션의 문서 처리 및 대화 기능을 크게 향상시켰습니다. 이러한 기능을 시연하기 위해 새로운 애플리케이션 `rag_gradio_llamaparser_app.py`가 생성되었습니다.

## 핵심 개선 사항

-   **LlamaParse 통합을 통한 강력한 문서 처리:**
    -   `PyMuPDF`에서 `LlamaParse`로 전환하여 PDF 문서를 파싱합니다. `LlamaParse`는 복잡한 레이아웃, 특히 표 추출에 뛰어나 RAG 시스템에 더 깨끗하고 정확한 입력을 보장합니다.
    -   캐싱 메커니즘을 구현했습니다: `LlamaParse`를 한 번만 호출하여 PDF를 마크다운 파일(`llamaparse_output_full.md`)로 변환합니다. 이후 실행 시 캐시된 마크다운에서 로드하여 API 호출과 시작 시간을 크게 단축합니다.

-   **기록 인식 리트리버를 사용한 대화형 메모리:**
    -   `History-Aware Retriever`를 통합하여 RAG 챗봇이 대화의 이전 내용을 기억할 수 있도록 했습니다.
    -   이제 시스템이 대화 기록을 기반으로 후속 질문을 지능적으로 재구성하여, 더 관련성 높은 문서를 검색하고 일관된 답변을 보장합니다.
    -   더 모듈화되고 견고한 아키텍처를 위해 LangChain Expression Language (LCEL)를 사용하여 RAG 체인을 리팩토링했습니다.

## 새로운 애플리케이션

-   **`rag_gradio_llamaparser_app.py`:** LlamaParse 통합 및 대화형 메모리 기능을 보여주는 새로운 Gradio 애플리케이션입니다. 이 애플리케이션은 향상된 RAG 파이프라인의 주요 예시 역할을 합니다.

---

# 업데이트 로그 v1.4

이번 버전은 단순성과 견고성을 위한 주요 UI 리팩토링, 이전에 계획된 코드 업데이트 완료, 핵심 라이브러리 사용 표준화에 중점을 둡니다.

## UI 리팩토링

- **`gr.ChatInterface` 채택:** Gradio UI를 고수준 `gr.ChatInterface` 컴포넌트를 사용하도록 리팩토링했습니다. 이를 통해 수동 `gr.Blocks`, `gr.Textbox`, `gr.Button` 이벤트 처리의 필요성을 제거하여 애플리케이션 코드를 크게 단순화했습니다. 이제 `gr.ChatInterface`가 채팅 흐름, 기록, 입력 제출을 기본적으로 관리하여 더 견고하고 유지보수하기 쉬운 코드를 구현합니다.

## 핵심 로직 및 라이브러리 업데이트

- **리팩토링 완료 (`.invoke()`):** v1.2에서 보류 중이던 리팩토링이 완료되었습니다. 이제 리트리버는 레거시 `get_relevant_documents()` 메소드 대신 `retriever.invoke(query)`를 사용하여 호출됩니다.
- **표준화된 PDF 처리 (PyMuPDF):** PDF 처리 로직은 이제 안정적인 텍스트 추출을 위해 최신 메소드(`page.get_text("text")`)와 함께 `PyMuPDF` (`fitz`) 라이브러리를 명시적이고 일관되게 사용합니다.
- **LLM 업데이트:** 모델이 `gpt-4o-mini`로 업데이트되어 성능과 비용 효율성이 향상되었습니다.

---

# 업데이트 로그 v1.3

이번 버전은 자체 복구 메커니즘의 심각한 런타임 오류를 수정하고 라이브러리 의존성 경고를 해결하는 데 중점을 둡니다.

## 버그 수정

- **자가 복구 시 `PermissionError: [WinError 32]` 발생:** 자체 복구 메커니즘이 ChromaDB 디렉토리를 삭제하려고 할 때 발생하던 파일 잠금 문제를 해결했습니다. 파일 시스템 수준의 삭제(`shutil.rmtree`) 대신 더 안정적인 API 호출(`vectorstore.delete_collection()`)을 사용하여 파일 접근 충돌 없이 데이터베이스 컬렉션을 올바르게 리셋하도록 수정했습니다.

## 개선 및 경고 수정

- **Gradio 의존성 경고:** `gr.Chatbot` 컴포넌트에 `type='messages'`를 설정하여 `UserWarning`을 해결하고 최신 Gradio 표준에 맞게 조정했습니다.
- **LangChain Chroma 의존성 경고:** `Chroma` import 경로를 `langchain_community.vectorstores`에서 `langchain_chroma`로 업데이트하여 `LangChainDeprecationWarning`을 해결하고 최신 패키지를 사용하도록 수정했습니다.

---

# 업데이트 로그 v1.2

이번 버전은 추가적인 버그 수정, 안정성 향상 및 UI 개선을 포함합니다.

## 버그 수정

- **`SyntaxError: name 'vectorstore' is used prior to global declaration`:** `ask_llm` 함수의 시작 부분에 `vectorstore`와 `retriever`에 대한 `global` 선언을 올바르게 배치하고 중복 선언을 제거하여 해결했습니다.

## 개선

- **벡터 저장소 자가 복구:** 저장소가 채워져 있음에도 불구하고 관련 문서가 검색되지 않는 경우, ChromaDB 벡터 저장소를 자동으로 감지하고 다시 채우는 메커니즘을 구현했습니다. 이를 통해 일관성 없는 상태에 대한 안정성을 향상시켰습니다.
- **UI 개선 (영구 예시):** `gr.Blocks`와 `gr.Examples`를 사용하여 채팅 입력창 아래에 예시 질문을 영구적으로 표시하도록 Gradio 인터페이스를 수정하여 사용자 안내를 개선했습니다.

---

# 업데이트 로그 v1.1

이번 버전은 버그 수정 및 사소한 개선 사항을 포함합니다.

## 버그 수정

- **`AttributeError: 'dict' object has no attribute 'page_content''`:** 리트리버에 추가되는 문서가 사전(`dict`)이 아닌 적절한 `langchain.schema.Document` 객체인지 확인하여 해결했습니다.

## 개선

- **PDF 처리 페이지 제한:** 사용자 요구사항에 맞춰 `rag_gradio_app.py`에서 PDF 처리를 1-18페이지로 명시적으로 제한했습니다.
- **ChromaDB 의존성 경고:** LangChain에서 `Chroma` import 및 클래스 사용과 관련된 의존성 경고를 인지하고 기록했습니다. (코드 변경은 없지만 향후 업데이트를 위해 기록)

---

# 업데이트 로그 v1.0

이 문서는 버전 1.0까지 RAG 챗봇에 구현된 기능을 요약합니다.

## 핵심 기능

- **PDF 텍스트 추출:** PDF 문서에서 텍스트 콘텐츠를 추출합니다.
- **페이지 제한:** PDF의 1페이지부터 18페이지까지의 콘텐츠를 처리합니다.

## RAG 시스템 개선

- **텍스트 분할:** LangChain의 `RecursiveCharacterTextSplitter`를 사용한 고급 텍스트 분할을 구현했습니다.
- **임베딩 생성:** OpenAI의 `text-embedding-3-small` 모델을 사용하여 텍스트 청크에 대한 임베딩을 생성합니다.
- **벡터 저장소 (ChromaDB):** 임베딩과 텍스트 청크를 영구적인 ChromaDB 인스턴스(`./chroma_db` 디렉토리)에 저장합니다.
- **캐싱:** 벡터 저장소는 캐시됩니다. 이후 실행 시 ChromaDB가 이미 채워져 있으면 PDF 재처리 및 재임베딩을 건너뛰어 시작 시간을 단축합니다.
- **ParentDocumentRetriever:** 자식 청크 유사도를 기반으로 관련 부모 문서를 효율적으로 검색하기 위해 `ParentDocumentRetriever`를 활용합니다.

## 사용자 인터페이스 (Gradio)

- **대화형 챗봇:** PDF 콘텐츠에 대해 질문할 수 있는 Gradio 웹 인터페이스를 제공합니다.
- **한국어 지원:** LLM 프롬프트가 모델에게 한국어로 답변하도록 지시합니다. UI의 예시 질문도 한국어로 되어 있습니다.
