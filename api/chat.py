from fastapi import FastAPI
from services.rag import RAGRetriever
from services.embedding import EmbeddingManager
from services.chat_memory import ChatMemory
from services.vectorstore import VectorStore, Metadata
import uuid
from typing import Optional
app = FastAPI()

# api for conversational RAG
@app.get("/chat/")
def chat(query: str, sessionid:Optional[str] = None):
    try:
        # if sessionid is not provided, new id will be generated for each request
        # how to use:
        #   client donot provides sessionid for the first time
        #   server sends sessionid to client in response
        #   from second time, client needs to send sessionid otherwise new sessionid will be created for every request
        if not sessionid:
            sessionid = str(uuid.uuid4())

        metadata = Metadata() # for storing booking details 
        chat_memory = ChatMemory(sessionid = sessionid) # for maintaining chat history
        embedding_manager = EmbeddingManager() # for creating embeddings for query
        vector_store = VectorStore() # vector db where context is searched
        rag_retriever = RAGRetriever(metadata=metadata,chat_memory= chat_memory,embedding_manager=embedding_manager,vector_store=vector_store)
        response = rag_retriever.ret_aug_gen(query= query)
        response['sessionid'] = sessionid
        return response
    except Exception as e:
        return {"Error":f"{str(e)}"}
    


