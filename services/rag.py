import requests
import json
from dotenv import load_dotenv
import os
from typing import Dict
from services.embedding import EmbeddingManager
from services.vectorstore import VectorStore
from services.vectorstore import Metadata
from services.chat_memory import ChatMemory

load_dotenv() # Loads variables from .env into os.environ


class RAGRetriever:
    """
    Handles query based retrieval from vector store
    """
    def __init__(self,metadata:Metadata,chat_memory:ChatMemory,embedding_manager:EmbeddingManager,vector_store:VectorStore):
        """
        Description:
            Constructor to initialize the retriever
        Arguments:
            metadata = Metadata object
            chat_memory = ChatMemory object
            embedding_manager = EmbeddingManager object
            vector_store = VectorStore object
        """
        self.metadata = metadata
        self.chat_memory = chat_memory
        self.vector_store = vector_store
        self.embedding_manager = embedding_manager

    def retrieve(self, query:str, top_k:int) -> list[Dict]:
        """
        Description:
            Method to retrieve relevant documents/chunks for a query i.e, performs semantic search on vector database
        Arguments:
            query: the search query
            top_k: no. of top results to return
        Returns:
            List of dictionaries containing retrieved documents and metadata
        """
        print(f"Retrieving documents for query: {query}")

        # generate query embeddings
        query_embedding = self.embedding_manager.generate_embeddings([query])[0]

        # search in vector store
        try:
            results = self.vector_store.pinecone_index.query(
                vector=query_embedding.tolist(), 
                top_k=top_k,
                include_metadata=True,
                include_values=False
            )
            return results
        except Exception as e:
            print(f"Error during retrieval : {e}")
            return []
        
    def ret_aug_gen(self,query:str,top_k:int=3)->dict:
        """
        Description:
            Method for augmentation and generation
        Arguments:
            query: the search query
            top_k: no. of top results to return
        Returns:
            response dictionary
        """
        # retrieve the context
        results = self.retrieve(query=query,top_k=top_k)
        results = [each['metadata'] for each in results['matches']]
        context = "\n\n".join([each['text'] for each in results]) if results else "" # ternary operator not list comprehension with condition

        # using redis for chat memory
        history = self.chat_memory.get_chat_history()

        # system prompt for the llm
        booking_system_prompt = """
            Your job is to decide whether:
            1. the user wants to book an interview or,
            2. the user is asking a general question

            If the user is asking a general question:
            - Set route to "rag"
            - Answer using the provided context and conversation history
            - Put the answer in the "reply" field

            If the user wants to book an interview:
            - Set route to "booking"
            - Extract the following fields:
                - name
                - email
                - date
                - time

            Rules:
            - Respond ONLY in valid JSON
            - JSON fields must be exactly: route, booking, reply
            - If a booking field is missing or unclear, set that field to null. Do NOT guess missing booking fields
            - Convert dates to YYYY-MM-DD
            - Convert times to 24-hour HH:MM
            - If route is "booking", reply must be null
            - If route is "rag", booking must be null
            """
        # user prompt for the llm 
        prompt = f"""
                Conversation so far:
                {history}

                Context:
                {context}
                
                Query:
                {query}
                """
        # print(prompt)
        OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") # access variables
        response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            # "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
            # "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
        },
        data=json.dumps({
            "model": "stepfun/step-3.5-flash:free",
            # "model": "liquid/lfm-2.5-1.2b-thinking:free",
            "messages": [
            {"role": "system", "content": booking_system_prompt},
            {
                "role": "user",
                "content": prompt
            }
            ],
            "reasoning": {"enabled": True}
        })
        )
        # print(response.json())
        # print(type(json.loads(response.json())))

        hist = {"user":query,"assistance":None}
        try:
            output  = json.loads(response.json()['choices'][0]['message']['content'])
            print(output)
        except Exception as e:
            print(f"error: {str(e)}")
            hist['assistance'] = f"Something went wrong during response parsing. Try to give clear prompts."
            return hist

        if output['route'] == "booking":
            if output["booking"] is not None:
                missing_fields = [k for k,v in output["booking"].items() if v is None] # fields having none values
                if len(missing_fields) != 0:
                    hist["assistance"] = f"Please provide the missing fields: {','.join(missing_fields)}"
                    self.chat_memory.save_chat_history(history= hist)
                    return hist
                else:
                    # print(output['booking'])
                    # saving the booking details in the same sql database of metadata
                    # save the booking details
                    response = self.metadata.write_booking_details(output["booking"])
                    if response is None:
                        hist["assistance"] = "Your interview is scheduled successfully"
                        self.chat_memory.save_chat_history(history= hist)
                        return hist
                    else:
                        hist['assistance'] = response['Message']
                        return hist
                        
            else:
                all_fields = ["name","email","date","time"]
                hist['assistance'] = f"Please provide the missing fields: {','.join(all_fields)}"
                self.chat_memory.save_chat_history(history= hist)
                return hist
        elif output["route"] == "rag":
            hist["assistance"] = output["reply"]
            self.chat_memory.save_chat_history(history= hist)
            return hist

# if __name__ == "__main__":
#     rag_retriever = RAGRetriever()
#     # response = rag_retriever.ret_aug_gen(query="Did he get certification from any college or institution? If yes what is the name of the institution")
#     # response = rag_retriever.ret_aug_gen(query="What skillsets has he got?")
#     response = rag_retriever.ret_aug_gen(query="What is his contact number?")
#     print("\n\n")
#     print(response['assistance'])