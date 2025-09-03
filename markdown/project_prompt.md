# 🚀 미니프로젝트2 - 뉴스 요약 & 해시태그 사이트

## 1. 목표 (MVP)
- **Gradio 기반 웹사이트**에서 뉴스 URL 입력 시:
  - 기사 본문 추출
  - 핵심 요약(3~5 bullet, 20~30자 내)
  - 해시태그(3~6개, 일반적 단어 제외)
  - (선택) 근거 문장 인용
- 추가: 해시태그 로그를 저장 → 개인화된 뉴스 추천(네이버 뉴스 API 연동)

---

## 2. 기술 스택
- **로더**: `WebBaseLoader`
- **스플리터**:  
  - `HTMLHeaderTextSplitter` (h1,h2,h3 기준)  
  - `kss` 문장 단위 병합 (400~600자)  
  - `RecursiveCharacterTextSplitter` (chunk_size 900~1200, overlap 120~160)
- **임베딩**: Upstage Embedding (또는 OpenAI Embeddings)  
- **벡터 저장소**: `ChromaDB`  
- **리트리버**: 기본 similarity (top_k=4), 필요시 BM25/앙상블 적용  
- **LLM 활용**:  
  - 요약: bullet 3~5개, 20~30자  
  - 해시태그: 3~6개 (#뉴스, #이슈 제외)  
- **API**: 네이버 뉴스 검색 API (추천 기사 수집/확장)

---

## 3. 개인화 추천 로직
1. 요약 완료 시 생성된 **해시태그 로그 적재**
   - `{article_id, url, title, published_at, tags[]}`
   - 사용자 태그 통계(`count`, `last_seen`, `decayed_score`) 관리
2. 태그 간 **공동출현(co-occurrence)** 기록 → 연관 태그 그래프 구축
3. 매일 **감쇠 점수 계산**: 최근 관심사를 반영
4. 추천 프로세스:
   - Top-N 개인 태그 + 연관 태그 k개 선택
   - 네이버 뉴스 API로 검색
   - 중복 제거 후 “오늘의 개인화 Top 5” 카드 구성

---

## 4. Gradio UI 구성
- **입력 칸**: 뉴스 URL
- **출력 영역**: 
  - 기사 제목
  - 요약 bullet (3~5)
  - 해시태그 (칩 형태)
  - (선택) 근거 문장
- **개인화 탭**:
  - 내가 자주 보는 태그(점수/횟수 표시)
  - 오늘의 개인화 추천 기사 Top 5

---

## 5. 모듈 구조 제안
project_root/
├─ app/
│ └─ ui.py (Gradio 인터페이스)
├─ api/
│ ├─ loader.py
│ ├─ splitter.py
│ ├─ summarize.py
│ ├─ tagger.py
│ └─ naver_search.py
├─ retriever/
│ └─ personalize.py
├─ data/
│ ├─ store.py (SQLite/JSONL)
│ └─ batch_recalc.py (감쇠·연관 업데이트)
└─ .env (NAVER_CLIENT_ID, NAVER_CLIENT_SECRET)
---

## 6. 다음 단계
1. `.env`에 네이버 API 키 설정
2. `splitter.py` 구현 (헤더→문장→토큰)
3. Gradio 뼈대 (`ui.py`) 작성
4. 태그 로그 적재 + 개인 태그 통계 관리
5. 네이버 API 연동 → 개인화 추천 기사 출력