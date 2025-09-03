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

## 보류 중인 코드 리팩토링 (향후 버전 계획)

- **import 정리:** 중복된 import 문을 제거합니다.
- **LangChain 의존성 업데이트:** `Chroma` import를 `langchain.vectorstores`에서 `langchain_community.vectorstores`로 업데이트하고 `vectorstore.persist()` 호출을 제거합니다.
- **Retriever 메소드 업데이트:** `retriever.get_relevant_documents(query)`를 `retriever.invoke(query)`로 변경합니다.

---

# 업데이트 로그 v1.1

이번 버전은 버그 수정 및 사소한 개선 사항을 포함합니다.

## 버그 수정

- **`AttributeError: 'dict' object has no attribute 'page_content'`:** 리트리버에 추가되는 문서가 사전(`dict`)이 아닌 적절한 `langchain.schema.Document` 객체인지 확인하여 해결했습니다.

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
  - 부모 청크 (LLM 컨텍스트용): `chunk_size=2000`, `chunk_overlap=200`
  - 자식 청크 (임베딩 및 검색용): `chunk_size=400`, `chunk_overlap=40`
- **임베딩 생성:** OpenAI의 `text-embedding-3-small` 모델을 사용하여 텍스트 청크에 대한 임베딩을 생성합니다.
- **벡터 저장소 (ChromaDB):** 임베딩과 텍스트 청크를 영구적인 ChromaDB 인스턴스(`./chroma_db` 디렉토리)에 저장합니다.
- **캐싱:** 벡터 저장소는 캐시됩니다. 이후 실행 시 ChromaDB가 이미 채워져 있으면 PDF 재처리 및 재임베딩을 건너뛰어 시작 시간을 단축합니다.
- **ParentDocumentRetriever:** 자식 청크 유사도를 기반으로 관련 부모 문서를 효율적으로 검색하기 위해 `ParentDocumentRetriever`를 활용합니다.
  - 상위 2개 자식 청크(`k=2`)를 검색하고 해당 부모 문서를 반환합니다.

## 사용자 인터페이스 (Gradio)

- **대화형 챗봇:** PDF 콘텐츠에 대해 질문할 수 있는 Gradio 웹 인터페이스를 제공합니다.
- **한국어 지원:** LLM 프롬프트가 모델에게 한국어로 답변하도록 지시합니다. UI의 예시 질문도 한국어로 되어 있습니다.

## 향후 작업 (v1.0에 아직 구현되지 않음)

- **이미지-텍스트 연관:** 이미지와 관련 텍스트 청크를 연결하여 멀티모달 RAG를 구현합니다.
- **테이블 추출:** 강력한 테이블 추출 및 서식 지정을 마크다운에 통합합니다.