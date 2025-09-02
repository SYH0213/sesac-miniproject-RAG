# app.py
# -*- coding: utf-8 -*-

# =====================================================================================
# (KO) 실행 가이드
# 1. 필수 패키지를 설치합니다.
#    pip install gradio langchain langchain_community readability-lxml trafilatura rank-bm25 keybert scikit-learn beautifulsoup4 lxml html5lib
# 2. 이 스크립트를 실행합니다.
#    python app.py
# 3. 웹 브라우저에서 http://127.0.0.1:7860 또는 http://0.0.0.0:7860 주소로 접속합니다.
#
# (EN) Execution Guide
# 1. Install the required packages.
#    pip install gradio langchain langchain_community readability-lxml trafilatura rank-bm25 keybert scikit-learn beautifulsoup4 lxml html5lib
# 2. Run this script.
#    python app.py
# 3. Open your web browser and go to http://127.0.0.1:7860 or http://0.0.0.0:7860.
# =====================================================================================

import gradio as gr
import time
import os
from urllib.parse import urlparse

# =====================================================================================
# (KO) 의존성 임포트 시도 및 예외 처리
# (EN) Attempt to import dependencies and handle exceptions
# =====================================================================================
try:
    from langchain_community.document_loaders import WebBaseLoader, AsyncHtmlLoader, RequestsLoader
    from langchain_community.document_transformers import Html2TextTransformer
    from readability import Document as ReadabilityDocument
    import trafilatura
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from rank_bm25 import BM25Okapi
    from keybert import KeyBERT
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("(경고/Warning) LangChain 또는 관련 라이브러리를 찾을 수 없습니다. 규칙 기반의 간단한 폴백 모드로만 작동합니다.")
    print("(경고/Warning) LangChain or related libraries not found. Operating in simple rule-based fallback mode only.")


# =====================================================================================
# (KO) 파이프라인 스텁 (v0)
# (EN) Pipeline Stub (v0)
# =====================================================================================

def get_domain(url):
    """Extracts the domain from a URL."""
    try:
        return urlparse(url).netloc
    except Exception:
        return "unknown"

def rule_based_summarize(text, length_mode='medium', style='paragraph', bullet_count=5):
    """A simple rule-based summarizer."""
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 10]
    if not sentences:
        return "요약할 내용이 없습니다." if style == 'paragraph' else "- 요약할 내용이 없음"

    total_sentences = len(sentences)
    if length_mode == 'short':
        num_sentences = min(2, total_sentences)
    elif length_mode == 'medium':
        num_sentences = min(5, total_sentences)
    else: # 'long'
        num_sentences = min(10, total_sentences)

    summary_sentences = sentences[:num_sentences]

    if style == 'bullets':
        return "\n".join([f"- {s}" for s in summary_sentences[:bullet_count]])
    else:
        return ". ".join(summary_sentences) + "."

def rule_based_hashtags(text, count=6, lang='ko', dedupe=True):
    """A simple rule-based hashtag generator."""
    words = [w.strip('.,!"?') for w in text.split() if len(w.strip('.,!"?')) > 1]
    if not words:
        return []

    # Simple frequency count
    from collections import Counter
    word_counts = Counter(words)
    top_words = [word for word, freq in word_counts.most_common(count)]

    return [f"#{word}" for word in top_words]


def pipeline_run(url, length_radio, style_radio, bullet_slider, tag_count, tag_lang, tag_dedupe,
                 loader_select, min_para_len, top_k, reranker_select, evidence_n, use_cache):
    """
    (KO) v0 프로토타입의 메인 파이프라인 함수. 실제 로직은 대부분 스텁 처리됩니다.
    (EN) Main pipeline function for the v0 prototype. Most logic is stubbed.
    """
    start_time = time.time()
    timings = {}
    debug_log = []
    fallback_chain = []
    loader_used = "N/A"
    cleaned_text = ""
    raw_chars = 0
    clean_chars = 0
    title = "제목을 찾을 수 없음"

    # --- Step 1: Fetch/Parse ---
    fetch_start = time.time()
    docs = []
    if LANGCHAIN_AVAILABLE and loader_select != 'Auto(Fallback)':
        try:
            loader_used = 'WebBaseLoader'
            debug_log.append(f"[INFO] 1. Trying {loader_used}...")
            loader = WebBaseLoader([url])
            docs = loader.load()
            title = docs[0].metadata.get('title', title)
            fallback_chain.append(f"{loader_used}: Success")
        except Exception as e:
            debug_log.append(f"[ERROR] {loader_used} failed: {e}")
            fallback_chain.append(f"{loader_used}: Fail")
            docs = [] # Ensure docs is empty for fallback

    if not docs: # Fallback logic
        loader_used = 'Auto(Fallback)'
        debug_log.append(f"[INFO] 1a. Fallback initiated.")
        try:
            fallback_chain.append("AsyncHtmlLoader: Attempt")
            debug_log.append("[INFO] Trying AsyncHtmlLoader + Readability...")
            async_loader = AsyncHtmlLoader([url])
            html_docs = async_loader.load()
            # This is a simplification. Real readability would be more complex.
            html2text = Html2TextTransformer()
            docs = html2text.transform_documents(html_docs)
            if not docs or not docs[0].page_content.strip():
                raise ValueError("Empty content from AsyncHtmlLoader")
            debug_log.append("[INFO] AsyncHtmlLoader success.")
            fallback_chain[-1] = "AsyncHtmlLoader: Success"
        except Exception as e:
            debug_log.append(f"[ERROR] AsyncHtmlLoader failed: {e}")
            fallback_chain[-1] = "AsyncHtmlLoader: Fail"
            try:
                fallback_chain.append("trafilatura: Attempt")
                debug_log.append("[INFO] Trying trafilatura...")
                fetched = trafilatura.fetch_url(url)
                content = trafilatura.extract(fetched, include_comments=False, include_tables=False)
                if not content:
                     raise ValueError("Empty content from trafilatura")
                from langchain_core.documents import Document
                docs = [Document(page_content=content, metadata={'source': url})]
                debug_log.append("[INFO] trafilatura success.")
                fallback_chain[-1] = "trafilatura: Success"
            except Exception as e_traf:
                debug_log.append(f"[ERROR] trafilatura failed: {e_traf}")
                fallback_chain[-1] = "trafilatura: Fail"
                docs = [Document(page_content="문서 로드에 실패했습니다. URL을 확인하거나 다른 로더를 시도해보세요.", metadata={})]


    timings['fetch'] = int((time.time() - fetch_start) * 1000)
    raw_text = docs[0].page_content if docs else ""
    raw_chars = len(raw_text)

    # --- Step 2: Clean ---
    clean_start = time.time()
    # Simple cleaning: just use the text as is for v0
    cleaned_text = raw_text
    paragraphs = [p.strip() for p in cleaned_text.split('\n') if len(p.strip()) >= min_para_len]
    cleaned_text = "\n\n".join(paragraphs)
    clean_chars = len(cleaned_text)
    debug_log.append(f"[INFO] 2. Cleaned text, paragraphs: {len(paragraphs)}")
    timings['clean'] = int((time.time() - clean_start) * 1000)


    # --- Step 3: Select ---
    select_start = time.time()
    # Simple selection: take top_k paragraphs
    context_paras = paragraphs[:top_k]
    context = "\n".join(context_paras)
    debug_log.append(f"[INFO] 3. Selected top {len(context_paras)} paragraphs for context.")
    timings['select'] = int((time.time() - select_start) * 1000)

    # --- Step 4: Summarize ---
    summarize_start = time.time()
    summary_short = rule_based_summarize(context, 'short', style_radio, bullet_slider)
    summary_medium = rule_based_summarize(context, 'medium', style_radio, bullet_slider)
    summary_long = rule_based_summarize(context, 'long', style_radio, bullet_slider)
    debug_log.append(f"[INFO] 4. Generated 3 summaries (rule-based).")
    timings['summarize'] = int((time.time() - summarize_start) * 1000)

    # --- Step 5: Hashtags ---
    hashtag_start = time.time()
    if LANGCHAIN_AVAILABLE and cleaned_text:
         kw_model = KeyBERT()
         keywords = kw_model.extract_keywords(cleaned_text, keyphrase_ngram_range=(1, 1), stop_words=None, top_n=tag_count)
         hashtags = [f"#{kw[0]}" for kw in keywords]
    else:
        hashtags = rule_based_hashtags(cleaned_text, tag_count, tag_lang, tag_dedupe)

    debug_log.append(f"[INFO] 5. Generated {len(hashtags)} hashtags.")
    timings['post'] = int((time.time() - hashtag_start) * 1000) # Re-using timing slot

    # --- Step 6: Evidence ---
    evidence_start = time.time()
    evidence = []
    if evidence_n > 0 and context_paras:
        evidence = [{"sentence": para, "para_index": i} for i, para in enumerate(context_paras[:evidence_n])]
    debug_log.append(f"[INFO] 6. Extracted {len(evidence)} evidence paragraphs.")
    timings['evidence'] = int((time.time() - evidence_start) * 1000)


    # --- Final Result Assembly ---
    total_time = int((time.time() - start_time) * 1000)
    debug_log.append(f"\n--- 총 처리 시간: {total_time}ms ---")
    debug_output = "\n".join(debug_log)

    result = {
        "url": url,
        "title": title,
        "summaries": {"short": summary_short, "medium": summary_medium, "long": summary_long},
        "hashtags": hashtags,
        "evidence": evidence,
        "cleaned_text": cleaned_text,
        "debug": {
            "loader_used": loader_used,
            "fallback_chain": fallback_chain,
            "timings_ms": timings,
            "lengths": {"raw_chars": raw_chars, "clean_chars": clean_chars},
            "log": debug_output
        }
    }
    
    # (KO) Gradio 출력에 맞게 변환
    # (EN) Convert to Gradio outputs
    return (
        gr.update(value=result["summaries"]["short"]),
        gr.update(value=result["summaries"]["medium"]),
        gr.update(value=result["summaries"]["long"]),
        gr.update(value=", ".join(result["hashtags"])),
        gr.update(value=result["evidence"]),
        gr.update(value=result["cleaned_text"]),
        gr.update(value=result["debug"]["log"])
    )

# =====================================================================================
# (KO) Gradio UI 레이아웃
# (EN) Gradio UI Layout
# =====================================================================================

def load_sample_urls():
    """Loads URLs from URL_sample.txt if it exists."""
    sample_file = "URL_sample.txt"
    if os.path.exists(sample_file):
        with open(sample_file, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
            return urls
    return []

def create_ui():
    sample_urls = load_sample_urls()

    with gr.Blocks(theme=gr.themes.Soft(), title="뉴스 요약 프로토타입") as demo:
        gr.Markdown("# Gemini-CLI 뉴스 요약 프로토타입 (v0)")

        with gr.Row():
            with gr.Column(scale=4): # Left column for inputs
                gr.Markdown("### 입력 및 옵션")
                url_in = gr.Textbox(label="뉴스 URL 입력", placeholder="https://n.news.naver.com/...")

                with gr.Row():
                    btn_load_samples = gr.Dropdown(sample_urls, label="샘플 URL 불러오기", visible=bool(sample_urls))
                    btn_paste = gr.Button("붙여넣기")
                
                btn_run = gr.Button("요약 실행 ▶", variant="primary")

                with gr.Accordion("요약 옵션", open=True):
                    length_radio = gr.Radio(['short', 'medium', 'long'], label="요약 길이", value='medium')
                    style_radio = gr.Radio(['paragraph', 'bullets'], label="출력 형식", value='paragraph')
                    bullet_slider = gr.Slider(3, 7, step=1, value=5, label="불릿 수 (bullets 형식 선택 시)")

                with gr.Accordion("해시태그 옵션", open=True):
                    tag_count = gr.Slider(3, 10, step=1, value=6, label="해시태그 개수")
                    tag_lang = gr.Radio(['ko', 'mix'], label="언어", value='ko')
                    tag_dedupe = gr.Checkbox(value=True, label="동의어 병합 (v0 미구현)")

                with gr.Accordion("고급 설정 (v0 스텁)", open=False):
                    loader_select = gr.Dropdown(['WebBaseLoader', 'Auto(Fallback)'], value='WebBaseLoader', label="로더")
                    min_para_len = gr.Slider(0, 300, step=10, value=40, label="최소 문단 길이 (자)")
                    top_k = gr.Slider(3, 10, step=1, value=5, label="Top-k 문단")
                    reranker_select = gr.Dropdown(['none', 'jina', 'cohere', 'upstage'], value='none', label="Re-ranker (미사용)")
                    evidence_n = gr.Slider(0, 5, step=1, value=0, label="근거 문장 개수")
                    use_cache = gr.Checkbox(value=True, label="캐시 사용 (미구현)")
                    # These are just for show in v0
                    model_provider = gr.Dropdown(['none'], value='none', label="모델 프로바이더 (프로토타입)")
                    temperature = gr.Slider(0.0, 1.0, step=0.1, value=0.2, label="Temperature")
                    max_tokens = gr.Slider(128, 2048, step=64, value=512, label="Max tokens")


            with gr.Column(scale=6): # Right column for results
                with gr.Tabs() as tabs:
                    with gr.TabItem("요약", id=0):
                        gr.Markdown("### 요약 결과")
                        with gr.Row():
                             btn_resummarize = gr.Button("선택된 길이로 재요약 (v0 미구현)")
                        out_short = gr.Textbox(label="짧은 요약 (Short)", lines=3, interactive=False)
                        out_medium = gr.Textbox(label="보통 요약 (Medium)", lines=8, interactive=False)
                        out_long = gr.Textbox(label="긴 요약 (Long)", lines=15, interactive=False)

                    with gr.TabItem("해시태그", id=1):
                        gr.Markdown("### 추천 해시태그")
                        out_tags = gr.Textbox(label="해시태그", interactive=False)
                        with gr.Row():
                            btn_copy_tags = gr.Button("해시태그 복사")
                            btn_copy_csv = gr.Button("CSV로 복사")

                    with gr.TabItem("근거 문장", id=2):
                        gr.Markdown("### 근거 문장 (Evidence)")
                        out_evidence_table = gr.Dataframe(headers=["para_index", "sentence"], interactive=False)

                    with gr.TabItem("전체 본문", id=3):
                        gr.Markdown("### 정제된 전체 본문 (Cleaned Full Text)")
                        out_fulltext = gr.Textbox(label="본문", lines=20, interactive=False)

                    with gr.TabItem("디버그", id=4):
                        gr.Markdown("### 디버그 로그")
                        out_debug_log = gr.Textbox(label="로그", lines=20, interactive=False)

        # (KO) 이벤트 바인딩
        # (EN) Event Binding
        
        # "붙여넣기" 버튼 클릭 시 클립보드 내용으로 URL 입력창 채우기
        btn_paste.click(
            fn=lambda: gr.update(value=gr.Clipboard().read()),
            outputs=url_in
        )
        
        # 샘플 URL 드롭다운 변경 시 URL 입력창에 반영
        btn_load_samples.change(
            fn=lambda url: gr.update(value=url),
            inputs=btn_load_samples,
            outputs=url_in
        )

        # "요약 실행" 버튼 클릭 시 파이프라인 실행
        btn_run.click(
            fn=pipeline_run,
            inputs=[url_in, length_radio, style_radio, bullet_slider, tag_count, tag_lang, tag_dedupe,
                    loader_select, min_para_len, top_k, reranker_select, evidence_n, use_cache],
            outputs=[out_short, out_medium, out_long, out_tags, out_evidence_table, out_fulltext, out_debug_log]
        )
        
        # (KO) 더미 버튼에 대한 클립보드 복사 기능 연결
        # (EN) Connect clipboard copy functionality for dummy buttons
        btn_copy_tags.click(fn=lambda x: gr.Clipboard.copy(x), inputs=out_tags, outputs=None)
        
    return demo

# =====================================================================================
# (KO) 애플리케이션 실행
# (EN) Application Execution
# =====================================================================================
if __name__ == "__main__":
    app_ui = create_ui()
    app_ui.launch(server_name="0.0.0.0", server_port=7860)
