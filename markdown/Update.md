# Update Log v1.5

This version introduces significant enhancements to the RAG application's document processing and conversational capabilities. A new application, `rag_gradio_llamaparser_app.py`, has been created to demonstrate these features.

## Core Enhancements

-   **LlamaParse Integration for Robust Document Processing:**
    -   Switched from `PyMuPDF` to `LlamaParse` for PDF document parsing. `LlamaParse` provides superior extraction of complex layouts, especially tables, ensuring cleaner and more accurate input for the RAG system.
    -   Implemented a caching mechanism: `LlamaParse` is called only once to convert the PDF into a Markdown file (`llamaparse_output_full.md`). Subsequent runs of the application load from this cached Markdown, significantly reducing API calls and startup time.

-   **Conversational Memory with History-Aware Retriever:**
    -   Integrated a `History-Aware Retriever` to enable the RAG chatbot to remember previous turns in the conversation.
    -   The system now intelligently rewrites follow-up questions based on chat history, ensuring more relevant document retrieval and coherent responses.
    -   The RAG chain has been refactored using LangChain Expression Language (LCEL) for a more modular and robust architecture.

## New Application

-   **`rag_gradio_llamaparser_app.py`:** A new Gradio application demonstrating the LlamaParse integration and conversational memory features. This application serves as the primary example for the enhanced RAG pipeline.

## Bug Fixes and Refinements

-   **Corrected Gradio History Parsing:** Resolved an issue where the `ask_llm` function incorrectly parsed Gradio's `ChatInterface` history format (list of dictionaries), leading to an empty `chat_history` being passed to the RAG chain. The function now correctly converts the history to LangChain's `HumanMessage`/`AIMessage` objects, ensuring proper conversational context.
-   **Fixed `qa_prompt` Typo:** Corrected a `NameError` caused by a typo (`ga_prompt` instead of `qa_prompt`) in the definition of the final answer generation prompt.
-   **Strengthened Hallucination Mitigation Prompt:** Enhanced the `qa_system_prompt` with more explicit instructions to the LLM to strictly adhere to the provided context and avoid generating information not present in the document.

---

# Update Log v1.4

This version focuses on a major UI refactoring for simplification and robustness, completes previously planned code updates, and standardizes core library usage.

## UI Refactoring

- **`gr.ChatInterface` Adoption:** The Gradio UI has been refactored to use the high-level `gr.ChatInterface` component. This significantly simplifies the application code by removing the need for manual `gr.Blocks`, `gr.Textbox`, and `gr.Button` event handling (`.click`, `.submit`, `.then`). The `gr.ChatInterface` now natively manages the chat flow, history, and input submission, leading to more robust and maintainable code.

## Core Logic & Library Updates

- **Refactoring Complete (`.invoke()`):** The pending refactoring from v1.2 has been completed. The retriever is now called using `retriever.invoke(query)` instead of the legacy `get_relevant_documents()` method.
- **Standardized PDF Processing (PyMuPDF):** The PDF processing logic now explicitly and consistently uses the `PyMuPDF` (`fitz`) library with modern methods (`page.get_text("text")`) for reliable text extraction.
- **LLM Update:** The model has been updated to `gpt-4o-mini` for improved performance and cost-effectiveness.

---

# Update Log v1.3

This version focuses on fixing a critical runtime error in the self-healing mechanism and addressing library deprecation warnings.

## Bug Fixes

- **`PermissionError: [WinError 32]` on Self-Healing:** Resolved a file locking issue that occurred when the self-healing mechanism tried to delete the ChromaDB directory. The fix replaces the file system-level deletion (`shutil.rmtree`) with a more robust API call (`vectorstore.delete_collection()`) to properly reset the database collection without causing file access conflicts.

## Improvements & Deprecation Fixes

- **Gradio Deprecation:** Set `type='messages'` in the `gr.Chatbot` component to resolve a `UserWarning` and align with modern Gradio standards.
- **LangChain Chroma Deprecation:** Updated the Chroma import from `langchain_community.vectorstores` to `langchain_chroma` to resolve a `LangChainDeprecationWarning` and use the latest package.

---

# Update Log v1.2

This version includes further bug fixes, robustness improvements, and UI enhancements.

## Bug Fixes

- **`SyntaxError: name 'vectorstore' is used prior to global declaration`:** Resolved by correctly placing the `global` declaration for `vectorstore` and `retriever` at the beginning of the `ask_llm` function, and removing redundant declarations.

## Improvements

- **Vector Store Self-Healing:** Implemented a mechanism to automatically detect and re-populate the ChromaDB vector store if no relevant documents are retrieved despite the store appearing populated. This enhances robustness against inconsistent states.
- **UI Enhancement (Permanent Examples):** Modified the Gradio interface to display example questions permanently below the chat input using `gr.Blocks` and `gr.Examples`, improving user guidance.

## Pending Code Refactoring (Planned for future versions)

- **Import Cleanup:** Remove duplicate import statements.
- **LangChain Deprecation Updates:** Update `Chroma` import from `langchain.vectorstores` to `langchain_community.vectorstores` and remove `vectorstore.persist()` calls.
- **Retriever Method Update:** Change `retriever.get_relevant_documents(query)` to `retriever.invoke(query)`.

---

# Update Log v1.1

This version includes bug fixes and minor improvements.

## Bug Fixes

- **`AttributeError: 'dict' object has no attribute 'page_content''`:** Resolved by ensuring that documents added to the retriever are proper `langchain.schema.Document` objects, not dictionaries.

## Improvements

- **PDF Processing Page Limit:** Explicitly limited PDF processing to pages 1-18 in `rag_gradio_app.py` to align with user requirements.
- **ChromaDB Deprecation Warnings:** Acknowledged and noted the deprecation warnings related to `Chroma` import and class usage in LangChain. (No code change, but noted for future updates).

---

# Update Log v1.0

This document summarizes the features implemented in the RAG chatbot up to version 1.0.

## Core Functionality

- **PDF Text Extraction:** Extracts text content from PDF documents.
- **Page Limit:** Processes content from pages 1 to 18 of the PDF.

## RAG System Enhancements

- **Text Splitting:** Implemented advanced text splitting using `RecursiveCharacterTextSplitter` from LangChain.
  - Parent chunks (for LLM context): `chunk_size=2000`, `chunk_overlap=200`
  - Child chunks (for embedding and retrieval): `chunk_size=400`, `chunk_overlap=40`
- **Embedding Generation:** Uses OpenAI's `text-embedding-3-small` model to generate embeddings for text chunks.
- **Vector Store (ChromaDB):** Stores embeddings and text chunks in a persistent ChromaDB instance (`./chroma_db` directory).
- **Caching:** The vector store is cached. On subsequent runs, if the ChromaDB is already populated, it skips reprocessing the PDF and re-embedding, leading to faster startup times.
- **ParentDocumentRetriever:** Utilizes `ParentDocumentRetriever` for efficient retrieval of relevant parent documents based on child chunk similarity.
  - Retrieves top-2 child chunks (`k=2`) and returns their corresponding parent documents.

## User Interface (Gradio)

- **Interactive Chatbot:** Provides a Gradio web interface for asking questions about the PDF content.
- **Korean Language Support:** LLM prompt instructs the model to answer in Korean. Example questions in the UI are also in Korean.

## Future Work (Not yet implemented in v1.0)

- **Image-Text Association:** Linking images with relevant text chunks for multimodal RAG.
- **Table Extraction:** Integrating robust table extraction and formatting into Markdown.