# 📰 미니프로젝트2: 네이버 뉴스 RAG 요약기

## 🎯 목표 (MVP)
- Gradio 기반 뉴스 분석 사이트 제작
- **입력**: 네이버 뉴스 API 검색어
- **처리**:
  1. 네이버 뉴스 API에서 기사 수집 (title + description)
  2. RAG 파이프라인 적용
     - 초기 k값 크게 가져오기 (예: 40개)
     - → rerank로 상위 m개만 추림 (예: 6~8개)
     - → 문장 단위 압축 (관련 문장만 남김)
  3. 최종 문맥을 LLM에 전달하여 요약 + 해시태그 생성
- **출력**:  
  - 기사 표 (제목 / 언론사 / 날짜 / 요약 / 해시태그 / 원문 링크)  
  - (옵션) 사용자 질문에 대한 답변 + 근거 문장 인용  

---

## ⚙️ 핵심 기능
- **검색 파라미터**: query, sort(sim|date), display(10~50), start
- **Rerank 전략**  
  1. 1차: `title+description` 기반 BM25 + Embedding 점수 → 상위 30개  
  2. 2차: 각 기사에서 질문 키워드 포함된 문장 주변 2~3문장만 추출  
  3. 3차: 크로스 인코더로 정밀 rerank → 상위 6~8개 선택  
- **문맥 압축**: 질문과 관련 없는 문장은 버리고 핵심만 남김  
- **토큰 예산 관리**: LLM에 넘기는 컨텍스트는 최대 2000토큰으로 제한  

---

## 🖥️ Gradio UI 구성
- 상단 입력 영역:  
  - 검색어(Text)  
  - 정렬(Radio: sim|date)  
  - 개수(Slider 10~50)  
  - 시작(Start Number)  
  - 검색 버튼  
- 좌측 결과 패널:  
  - 표(DataFrame): 제목 / 언론사 / 날짜 / 요약 / 해시태그 / 원문 링크  
- 우측 사이드:  
  - Q&A 입력칸 (검색 결과 기반 질문 가능)  
  - 옵션 토글:  
    - 중복 제거  
    - 카테고리 자동 태깅  
    - 시간 가중치 적용  
    - 출처 다양성 보장  
  - 프리셋 버튼: “타임라인 요약”, “모순 체크”, “핵심 수치만”  

---

## 📚 기술 스택
- **API**: Naver News API
- **문서 분할**: RecursiveCharacterTextSplitter  
- **임베딩**: Upstage Embedding (또는 OpenAI Embeddings)  
- **벡터DB**: Chroma  
- **Retriever**: EnsembleRetriever (Dense + BM25)  
- **재순위**: bge-reranker / Cohere ReRank  프로젝트 지침(Instructions)

이 프로젝트의 기본 지침과 계획은 `guidelines.md`를 참고한다.  
본 문서는 전체 개요 및 진행 상황만 요약한다.
- **압축**: ContextualCompressionRetriever + LLMChainExtractor  
- **LLM**: ChatOpenAI(gpt-4o-mini) 또는 Gemini  

---

## ✅ 기대 산출물
- Gradio 데모 앱 (뉴스 검색 → 요약/해시태그/질문 답변)  
- 문서 출력물  
  - `proposal.md` (프로젝트 개요)  
  - `prompt_templates.md` (요약/해시태그/근거 프롬프트 모음)  
  - `evaluation_plan.md` (간단한 평가 계획)  

---

## 🚀 다음 단계
1. 네이버 API 키 세팅 + 샘플 질의 테스트  
2. Gradio 입력칸 + 결과 표만 있는 기본 뼈대 제작  
3. RAG 모듈 연결 (rerank, 압축)  
4. Q&A/타임라인 등 확장 기능 붙이기  
