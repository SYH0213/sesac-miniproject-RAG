# 프로젝트 기술 스택 및 모델 정보

이 문서는 애플리케이션의 각 부분에서 사용된 주요 기술, 라이브러리, API 및 AI 모델에 대한 정보를 정리합니다.

---

### 1. `api/loader.py`
- **라이브러리**: `langchain_community.document_loaders`
- **핵심 기능**: `WebBaseLoader`
- **목적**: 지정된 URL의 웹 페이지(뉴스 기사) 콘텐츠를 로드하고 LangChain이 처리할 수 있는 `Document` 형식으로 변환합니다.

---

### 2. `api/splitter.py`
- **라이브러리**: `langchain_text_splitters`, `kss`
- **핵심 기능**: `HTMLHeaderTextSplitter`, `RecursiveCharacterTextSplitter`, `kss.split_sentences`
- **목적**: 로드된 HTML 문서를 먼저 헤더(h1, h2, h3) 기준으로 의미 단위로 분할하고, 이후 문장 단위로 분할(`kss`) 및 재귀적 문자 분할(`RecursiveCharacterTextSplitter`)을 통해 LLM이 처리하기 용이한 작은 텍스트 조각(chunk)으로 만듭니다.

---

### 3. `api/summarize.py`
- **라이브러리**: `langchain_upstage`, `langchain`
- **AI 모델**: `solar-1-mini-chat` (Upstage 제공)
- **핵심 기능**: `ChatUpstage`, `load_summarize_chain`
- **목적**: 분할된 텍스트 조각들을 입력받아 Upstage의 Solar 모델을 사용하여 핵심 내용을 3~5개의 bullet point로 요약합니다.

---

### 4. `api/tagger.py`
- **라이브러리**: `langchain_upstage`
- **AI 모델**: `solar-1-mini-chat` (Upstage 제공)
- **핵심 기능**: `ChatUpstage`, `PromptTemplate`
- **목적**: 기사 요약 내용을 기반으로, 미리 정의된 프롬프트를 통해 Upstage Solar 모델을 호출하여 3~6개의 관련 해시태그를 생성합니다.

---

### 5. `api/naver_search.py`
- **라이브러리**: `requests`
- **외부 API**: Naver Search API (News)
- **목적**: 사용자가 입력한 검색어를 쿼리로 사용하여 네이버 뉴스 API를 호출하고, 검색 결과(기사 제목, 링크)를 받아옵니다.

---

### 6. `data/store.py`
- **라이브러리**: `sqlite3`
- **목적**: 생성된 해시태그를 영구적으로 저장하기 위한 데이터베이스(`news_app.db`)를 관리합니다. 태그를 추가하고, 태그별 빈도수를 조회하는 기능을 제공합니다.

---

### 7. `retriever/personalize.py`
- **목적**: `data/store.py`에서 조회한 태그 빈도수를 기반으로 개인화 추천 로직을 수행합니다. 가장 자주 본 태그들을 키워드로 `naver_search.py`를 다시 호출하여 관련 높은 새로운 뉴스를 추천합니다.

---

### 8. `app/ui.py`
- **라이브러리**: `gradio`
- **목적**: 전체 애플리케이션의 사용자 인터페이스(UI)를 생성하고 관리합니다. 뉴스 검색, 기사 선택, 요약 및 해시태그 확인, 개인화 추천 확인 등 사용자와 상호작용하는 모든 시각적 요소를 담당하며, 백엔드 기능들과 연결하는 역할을 합니다.
