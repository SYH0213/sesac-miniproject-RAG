
# Gemini-CLI Prompt — Gradio 뉴스 요약 프로토타입 (v0)

> 아래 전체 블록을 **그대로** gemini-cli에 붙여 넣어주세요.  
> v0는 단일 파일(**app.py**)로 실행 가능한 프로토타입을 만듭니다.

```text
You are an expert Python engineer building a Gradio prototype from a product spec.
Follow ALL requirements exactly. Return ONLY code blocks for files as specified.
Use Korean labels for the UI but keep code comments bilingual (KO/EN).

# === Project Context ===
- Goal: 입력한 뉴스 URL을 로드/파싱하고, 길이 3단계 요약(짧게/보통/길게) + 해시태그를 출력하는 Gradio 프로토타입.
- Input files available in working dir (if present):
  - guidelines.md  (참고 자료)
  - URL_sample.txt (샘플 URL 목록; 한 줄당 1개 URL)
- Primary loader: LangChain **WebBaseLoader**.
  - Fallback A: **AsyncHtmlLoader + Readability**
  - Fallback B: **RequestsLoader + readability-lxml**
  - Last resort: **trafilatura** (직접 호출)
- Re-ranker는 v0에서 미사용(옵션 토글만 존재). Evidence(근거문장) n=0이 기본.

# === Deliverable ===
Produce ONE runnable Python file named **app.py** that contains:
1) Gradio UI layout (좌측 입력/옵션, 우측 탭 결과) 및 모든 컴포넌트/ID.
2) 이벤트 바인딩(버튼 클릭 → 파이프라인 실행, 퀵액션).
3) 파이프라인 스텁(실제 요약은 간단한 규칙 + LLM 호출은 함수형 인터페이스로만, 기본은 규칙기반).
4) 샘플 URL 로더(있으면 URL_sample.txt 읽어 드롭다운/리스트로 노출).
5) 디버그 탭(선택된 로더/폴백 단계, 처리시간, 길이, 에러 메시지 등).
6) 실행 가이드 주석(필요 패키지, 실행법).

Return exactly one code block:
```python
# app.py
# (code...)
```

# === Dependencies (document at top of file) ===
# pip install gradio langchain langchain-community readability-lxml trafilatura rank-bm25 keybert scikit-learn beautifulsoup4 lxml html5lib
# (requests, numpy, pandas는 필요 시만)
# Python 3.11+ 권장

# === UI Layout (must match) ===
# Header: 프로젝트명, [URL_sample.txt 불러오기], [도움말]
# Two-column:
#   Left (inputs/options, 40%)
#     - url_in: gr.Textbox(label="뉴스 URL 입력")
#     - btn_load_samples: gr.Button("URL_sample.txt 불러오기")
#     - btn_paste: gr.Button("붙여넣기")
#     - btn_run: gr.Button("요약 실행 ▶")
#     - 요약 옵션:
#         length_radio: gr.Radio(['short','medium','long'], label="요약 길이")
#         style_radio:  gr.Radio(['paragraph','bullets'], label="출력 형식")
#         bullet_slider: gr.Slider(3,7, step=1, value=5, label="불릿 수")
#     - 해시태그 옵션:
#         tag_count: gr.Slider(3,10, step=1, value=6, label="해시태그 개수")
#         tag_lang:  gr.Radio(['ko','mix'], label="언어", value='ko')
#         tag_dedupe: gr.Checkbox(value=True, label="동의어 병합")
#     - 고급(접기/펼치기):
#         loader_select: gr.Dropdown(['WebBaseLoader','Auto(Fallback)'], value='WebBaseLoader', label="로더")
#         min_para_len: gr.Slider(0,300, step=10, value=40, label="최소 문단 길이")
#         top_k:        gr.Slider(3,10, step=1, value=5, label="Top-k 문단")
#         reranker_select: gr.Dropdown(['none','jina','cohere','upstage'], value='none', label="Re-ranker(옵션)")
#         model_provider: gr.Dropdown(['none'], value='none', label="모델 프로바이더(프로토타입)")
#         temperature: gr.Slider(0.0,1.0, step=0.1, value=0.2, label="Temperature")
#         max_tokens: gr.Slider(128,2048, step=64, value=512, label="Max tokens")
#         evidence_n: gr.Slider(0,5, step=1, value=0, label="근거 문장 개수")
#         use_cache:  gr.Checkbox(value=True, label="캐시 사용")
#   Right (results, 60%) with tabs: Summary | Hashtags | Evidence | Full Text | Debug
#     - Summary: 3개의 카드(out_short, out_medium, out_long) + 각 복사 버튼 + "길이만 바꿔 재요약" 버튼
#     - Hashtags: out_tags (칩/텍스트), 복사/CSV복사 버튼
#     - Evidence: out_evidence_table (문장/문단 인덱스)
#     - Full Text: out_fulltext (정제된 본문 미리보기)
#     - Debug: out_debug_log (로더/폴백 단계, 시간, 길이, 오류 등)
# Footer: [JSON 내보내기], [Markdown 내보내기], [스크린샷] (버튼만, 동작은 스텁)

# === Event Flow ===
# btn_load_samples.click -> read URL_sample.txt -> 드롭다운/라디오(또는 Modal)로 선택 후 url_in에 반영
# btn_run.click -> pipeline_run(url, options) -> 결과 바인딩
# Quick actions on Summary: re-summarize with different length (no refetch/parse)
# Hashtag-only regenerate: same cleaned/chunks 기반으로 재생성

# === Pipeline (stub, must be implemented) ===
# pipeline_run(url, options):
#   timings = {}
#   step 1) fetch/parse:
#       try WebBaseLoader (domain allow, robots 준수) -> text
#       if fail -> AsyncHtmlLoader + Readability
#       if fail -> RequestsLoader + readability-lxml
#       if fail -> trafilatura.extract
#       record which loader_used + fallback_chain
#   step 2) clean:
#       - remove nav/footer/ads by simple heuristics (regex, tag filtering)
#       - split to paragraphs/sentences; filter len < min_para_len
#   step 3) select:
#       - rank paragraphs by BM25 vs title/lead if available
#       - take top_k as base context
#   step 4) summarize (rules-first, LLM-optional):
#       - short/medium/long: compress ratio templates
#       - if style == bullets: make bullet list of N=bullet_slider
#       - NO external API calls in v0; mimic with rule-based summarizer
#   step 5) hashtags:
#       - extract keywords via TF-IDF/KeyBERT (fallback TF-IDF only)
#       - normalize/merge synonyms if tag_dedupe
#       - tag_lang == 'mix'이면 1~2개 영문 태그 포함
#   step 6) evidence:
#       - evidence_n > 0 -> return top evidence_n sentences (with para_index)
#   step 7) post:
#       - de-duplicate n-grams, fix spacing, clamp length per mode
#   return ResultSchema with summaries/hashtags/evidence/cleaned_text/debug/timings

# === Result Schema (dict) ===
# {
#   "url": str, "title": str|None, "source_domain": str|None, "published_at": str|None,
#   "summaries": {"short": str, "medium": str, "long": str},
#   "hashtags": [str],
#   "evidence": [{"sentence": str, "para_index": int}],
#   "cleaned_text": str,
#   "debug": {
#       "loader_used": str, "fallback_chain": [str],
#       "timings_ms": {"fetch":int,"parse":int,"clean":int,"chunk":int,"select":int,"summarize":int,"post":int},
#       "lengths": {"raw_chars":int,"clean_chars":int}
#   }
# }

# === Edge Cases ===
# - 포토뉴스/속보: 본문이 매우 짧으면 제목+캡션 중심 요약 규칙으로 전환(배지 텍스트 포함).
# - 403/robots/본문 0자: 우측에 경고 카드 + 폴백 시도 메시지 + Debug 기록.
# - 중복·반복 문장: n-gram 반복 제거 후 Summary에 반영.

# === Acceptance Criteria ===
# - app.py 단독 실행 가능: `python app.py`
# - Gradio가 2열 레이아웃 및 5개 탭을 표시하고, 모든 버튼/슬라이더/라디오/체크박스가 존재.
# - btn_run 클릭 시 더미 요약/해시태그라도 즉시 채워짐(네트워크 실패해도).
# - Debug 탭에 선택된 로더/폴백/타이밍이 표시.
# - URL_sample.txt가 존재할 때 "불러오기"가 최소 1개 URL을 url_in에 주입.

# === Implementation Notes ===
# - 모듈 import 실패/네트워크 차단 환경에서도 실행되도록 각 단계 try/except로 방어하고, 규칙기반 더미 요약으로 폴백.
# - 코드 상단에 설치/실행 가이드를 주석으로 제공.
# - 한국어 UI 라벨(코드 내부 주석은 KO/EN 병기).
# - 기본값: length='medium', style='paragraph', tag_count=6, evidence_n=0, reranker='none'.

# === Run ===
# if __name__ == "__main__": launch(server_name="0.0.0.0", server_port=7860)