# Conversational RAG Backend (FastAPI + PyMySQL)

A modular backend for **document ingestion** and **conversational RAG** with multi-turn chat memory and interview booking.  

**Key Features:**  
- Upload `.pdf` / `.txt` documents  
- Two chunking strategies for text  
- Generate embeddings (Sentence Transformers="all-MiniLM-L6-v2")  
- Store metadata & booking info in **MySQL via PyMySQL**  
- Redis-based chat memory for multi-turn conversations  
- Custom RAG: Retrieve → Augment → Generate (no LangChain RetrievalQAChain)  

---

## Tech Stack
- **API:** FastAPI  
- **DB:** MySQL (PyMySQL)  
- **Vector DB:** Pinecone  
- **Memory:** Redis  
- **LLM:** OpenRouter LLM("stepfun/step-3.5-flash:free")

---
