# v1.1

## 주요 변경 사항

- **개발자용 기능 추가**: `news_app.db`에 저장된 해시태그 기록을 초기화할 수 있는 기능을 추가했습니다.

## 세부 작업 내역

### 1. 데이터 관리

- **`data/store.py`**: `hashtag_logs` 테이블의 모든 데이터를 삭제하는 `clear_hashtag_logs` 함수를 추가했습니다.

### 2. 사용자 인터페이스 (UI)

- **`app/ui.py`**: 
    - Gradio UI에 '개발자용' 탭을 새로 추가했습니다.
    - '개발자용' 탭 내부에 '해시태그 기록 초기화' 버튼을 배치하고, 해당 버튼 클릭 시 `clear_hashtag_logs` 함수가 실행되도록 연결했습니다.


# v1.0

## 주요 변경 사항

- **뉴스 검색 기능 추가**: URL을 직접 입력하는 대신, 키워드를 사용하여 네이버 뉴스에서 기사를 검색하는 기능으로 변경되었습니다.
- **UI 개선**: Gradio 인터페이스를 대대적으로 개편하여 '요약' 탭과 '개인화 추천' 탭으로 기능을 분리했습니다.
- **데이터베이스 연동**: 사용자가 생성한 해시태그를 SQLite 데이터베이스에 저장하여 개인화 추천의 기반을 마련했습니다.
- **개인화 추천 기능 구현**: 저장된 해시태그의 빈도를 분석하여, 사용자의 관심사에 맞는 새로운 뉴스를 추천하는 기능을 추가했습니다. (최소 10개 이상의 태그 데이터 필요)

## 세부 작업 내역

### 1. 프로젝트 구조 및 환경 설정

- `project_prompt.md`에 명시된 대로 `app`, `api`, `data`, `retriever` 디렉토리 구조를 설정했습니다.
- 각 디렉토리를 파이썬 패키지로 만들기 위해 `__init__.py` 파일을 추가했습니다.
- `requirements.txt` 파일에 `gradio`, `langchain`, `beautifulsoup4`, `kss`, `chromadb`, `langchain-upstage`, `python-dotenv`, `requests`, `fastapi`, `uvicorn`, `langchain-text-splitters` 등 프로젝트에 필요한 라이브러리를 명시하고 설치했습니다.
- 네이버 API 키 관리를 위한 `.env` 파일을 생성했습니다.

### 2. 핵심 기능 구현

- **`api/naver_search.py`**: 네이버 뉴스 API를 호출하여 특정 키워드로 뉴스를 검색하고, 결과(기사 제목, 링크)를 반환하는 `search_naver_news` 함수를 구현했습니다.
- **`api/loader.py`**: `WebBaseLoader`를 사용하여 주어진 URL의 뉴스 기사 본문을 불러오는 `load_article` 함수를 구현했습니다.
- **`api/splitter.py`**: `HTMLHeaderTextSplitter`와 `RecursiveCharacterTextSplitter`를 사용하여 기사 본문을 의미있는 단위로 분할하는 `split_text` 함수를 구현했습니다.
- **`api/summarize.py`**: Upstage Solar 모델을 활용하여 분할된 텍스트를 3~5개의 bullet point로 요약하는 `summarize_text` 함수를 구현했습니다.
- **`api/tagger.py`**: 요약된 내용을 기반으로 3~6개의 핵심 해시태그를 생성하는 `generate_tags` 함수를 구현했습니다.

### 3. 데이터 관리 및 개인화

- **`data/store.py`**: 
    - SQLite 데이터베이스(`news_app.db`)를 초기화하고 `hashtag_logs` 테이블을 생성하는 `initialize_db` 함수를 구현했습니다.
    - 생성된 해시태그를 데이터베이스에 추가하는 `add_tags` 함수를 구현했습니다.
    - 저장된 태그들의 빈도수를 계산하여 상위 태그를 반환하는 `get_tag_frequency` 함수를 구현했습니다.
- **`retriever/personalize.py`**: 
    - `get_tag_frequency` 함수를 호출하여 사용자의 상위 관심 태그를 파악합니다.
    - 데이터가 충분히 쌓였을 경우 (최소 10개), 해당 태그들을 키워드로 네이버 뉴스를 다시 검색하여 개인화된 추천 기사 목록을 반환하는 `get_personalized_recommendations` 함수를 구현했습니다.

### 4. 사용자 인터페이스 (UI)

- **`app/ui.py`**: 
    - Gradio의 `Blocks`와 `Tabs`를 사용하여 전체적인 UI 레이아웃을 구성했습니다.
    - **요약 탭**: 뉴스 검색창, 검색 결과 라디오 버튼, 요약 실행 버튼, 그리고 최종 요약 및 해시태그가 표시될 출력창을 배치했습니다.
    - **개인화 추천 탭**: 추천 목록을 불러오는 '새로고침' 버튼과 결과가 표시될 영역을 구현했습니다.
    - 각 UI 컴포넌트와 백엔드 기능(검색, 요약, 추천)을 유기적으로 연결하여 사용자의 입력에 따라 앱이 적절히 반응하도록 로직을 구현했습니다.