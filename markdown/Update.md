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