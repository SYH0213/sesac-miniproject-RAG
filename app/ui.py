import gradio as gr
import pandas as pd
from api.loader import load_article
from api.splitter import split_text
from api.summarize import summarize_text
from api.tagger import generate_tags
from api.naver_search import search_naver_news
from data.store import add_tags, clear_hashtag_logs
from retriever.personalize import get_personalized_recommendations

def search(query):
    articles = search_naver_news(query)
    if not articles:
        return pd.DataFrame({"제목": ["검색 결과가 없습니다."], "링크": [""]})
    df = pd.DataFrame(articles)
    df = df.rename(columns={"title": "제목", "link": "링크"})
    return df

def summarize_on_select(df, evt: gr.SelectData):
    if not isinstance(df, pd.DataFrame) or df.empty:
        return "기사 목록이 비어있습니다.", ""
        
    # Get the index of the selected row
    row_index = evt.index[0]
    
    # Get the link from the dataframe using the row index
    selected_link = df.iloc[row_index]["링크"]

    if not selected_link or not selected_link.startswith('http'):
        return "올바른 기사를 선택해주세요.", ""

    docs = load_article(selected_link)
    splits = split_text(docs)
    summary = summarize_text(splits)
    tags = generate_tags(summary)
    
    add_tags(tags)

    return summary, " #".join(tags)

def show_recommendations():
    recommendations = get_personalized_recommendations()
    if isinstance(recommendations, str):
        return gr.update(visible=True, value=recommendations), gr.update(visible=False)
    else:
        df = pd.DataFrame(recommendations)
        df = df.rename(columns={"title": "제목", "link": "링크"})
        return gr.update(visible=False), gr.update(visible=True, value=df)

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("<h1><center>📰 뉴스 요약 및 추천</center></h1>")

    with gr.Tabs():
        with gr.TabItem("요약"):
            with gr.Row():
                search_query = gr.Textbox(label="검색어", placeholder="관심있는 주제를 검색해보세요...", scale=4)
                search_button = gr.Button("검색", scale=1)
            
            with gr.Row():
                search_results_df = gr.Dataframe(
                    headers=["제목", "링크"], 
                    datatype=["str", "str"],
                    label="검색 결과",
                    interactive=False, # Rows are not editable, but selectable
                    row_count=(5, "dynamic"),
                    wrap=True
                )

            with gr.Row():
                summary_output = gr.Textbox(label="요약 결과", lines=5)
            with gr.Row():
                hashtags_output = gr.Textbox(label="추천 해시태그")

        with gr.TabItem("개인화 추천"):
            with gr.Column():
                refresh_button = gr.Button("추천 받기")
                recommendations_info = gr.Markdown(visible=False)
                recommendations_df = gr.Dataframe(
                    headers=["제목", "링크"], 
                    datatype=["str", "str"],
                    label="추천 기사",
                    interactive=False,
                    row_count=(5, "dynamic"),
                    wrap=True,
                    visible=False
                )
        
        with gr.TabItem("개발자용"):
            with gr.Column():
                clear_db_button = gr.Button("해시태그 기록 초기화")
                clear_db_message = gr.Markdown()

    # Event Listeners
    search_button.click(
        fn=search,
        inputs=search_query,
        outputs=search_results_df
    )

    import gradio as gr
import pandas as pd
from api.loader import load_article
from api.splitter import split_text
from api.summarize import summarize_text
from api.tagger import generate_tags
from api.naver_search import search_naver_news
from data.store import add_tags, clear_hashtag_logs
from retriever.personalize import get_personalized_recommendations
from retriever.retriever import create_retriever
from datetime import datetime

def search(query, sort, display, start):
    articles = search_naver_news(query, sort, display, start)
    if not articles:
        return pd.DataFrame({"제목": [""], "언론사": [""], "날짜": [""], "요약": [""], "해시태그": [""], "원문 링크": [""]})

    # Use the new retriever to get relevant documents
    retrieved_docs = create_retriever(articles, query)

    processed_articles = []
    for doc in retrieved_docs:
        article = doc.metadata # The original article dict is stored in metadata
        title = article.get("title", "")
        link = article.get("link", "")
        pub_date_str = article.get("pubDate", "")
        
        # Parse and format date
        formatted_date = ""
        try:
            dt_object = datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S %z")
            formatted_date = dt_object.strftime("%Y-%m-%d")
        except ValueError:
            pass

        publisher = "N/A" # Still N/A as Naver API doesn't provide it directly

        # RAG pipeline integration for retrieved documents
        docs_content = load_article(link)
        splits = split_text(docs_content)
        summary = summarize_text(splits)
        tags = generate_tags(summary)
        add_tags(tags)

        processed_articles.append({
            "제목": title,
            "언론사": publisher,
            "날짜": formatted_date,
            "요약": summary,
            "해시태그": ", ".join(tags),
            "원문 링크": link
        })
    
    df = pd.DataFrame(processed_articles)
    return df

def show_recommendations():
    recommendations = get_personalized_recommendations()
    if isinstance(recommendations, str):
        return gr.update(visible=True, value=recommendations), gr.update(visible=False)
    else:
        df = pd.DataFrame(recommendations)
        df = df.rename(columns={"title": "제목", "link": "링크"})
        return gr.update(visible=False), gr.update(visible=True, value=df)

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("<h1><center>📰 뉴스 요약 및 추천</center></h1>")

    with gr.Tabs():
        with gr.TabItem("요약"):
            with gr.Row():
                search_query = gr.Textbox(label="검색어", placeholder="관심있는 주제를 검색해보세요...", scale=4)
                sort_radio = gr.Radio(choices=["sim", "date"], label="정렬", value="sim", scale=1)
                display_slider = gr.Slider(minimum=10, maximum=50, value=10, step=1, label="개수", scale=1)
                start_number = gr.Number(minimum=1, value=1, label="시작", scale=1)
                search_button = gr.Button("검색", scale=1)
            
            with gr.Row():
                search_results_df = gr.Dataframe(
                    headers=["제목", "언론사", "날짜", "요약", "해시태그", "원문 링크"], 
                    datatype=["str", "str", "str", "str", "str", "str"],
                    label="검색 결과",
                    interactive=False,
                    row_count=(5, "dynamic"),
                    wrap=True
                )

        with gr.TabItem("개인화 추천"):
            with gr.Column():
                refresh_button = gr.Button("추천 받기")
                recommendations_info = gr.Markdown(visible=False)
                recommendations_df = gr.Dataframe(
                    headers=["제목", "링크"], 
                    datatype=["str", "str"],
                    label="추천 기사",
                    interactive=False,
                    row_count=(5, "dynamic"),
                    wrap=True,
                    visible=False
                )
        
        with gr.TabItem("개발자용"):
            with gr.Column():
                clear_db_button = gr.Button("해시태그 기록 초기화")
                clear_db_message = gr.Markdown()

    # Event Listeners
    search_button.click(
        fn=search,
        inputs=[search_query, sort_radio, display_slider, start_number],
        outputs=search_results_df
    )

    refresh_button.click(
        fn=show_recommendations,
        outputs=[recommendations_info, recommendations_df]
    )

    clear_db_button.click(
        fn=clear_hashtag_logs,
        outputs=clear_db_message
    )

if __name__ == "__main__":
    demo.launch()
