from services.chunking import Chunk
from services.embedding import EmbeddingManager
from pymysql import Connection
import numpy as np
import pinecone
import os
from datetime import datetime
import pymysql, uuid
import pymysql.cursors
from dotenv import load_dotenv
load_dotenv() # Loads variables from .env into os.environ


class Metadata:
    def __init__(self):
        """
        Description:
            Constructor to initialize database credentials
        """
        self.MYSQL_UID = os.getenv('MYSQL_UID')
        self.MYSQL_PWD = os.getenv('MYSQL_PWD')
        self.connection = None
        self.host = 'localhost'

    def _create_connection(self) -> Connection:
        """
        Description:
            Method to establish connection to the database
        Return:
            connection object
        """
        try:
            self.connection = pymysql.connect(
                    host= self.host,
                    user=self.MYSQL_UID,
                    password=self.MYSQL_PWD,
                    database='rag_metadata',
                    cursorclass=pymysql.cursors.DictCursor
                )
            return self.connection
        except Exception as e:
            raise Exception(f"Error in creating connection with sql: {str(e)}")
    
    def write(self,metadata:list) -> None:
        """
        Description:
            Method to write metadata to the database
        Arguments:
            metadata = list of metadata of embeddings
        """
        connection = self._create_connection()
        with connection:
            with connection.cursor() as cursor:
                for each in metadata:
                    cols = list(each.keys())
                    values = tuple(each.values())
                    cols_q = ", ".join(cols)
                    placeholders = ", ".join(['%s']*len(cols))
                    # print(cols)
                    # print(values)
                    query = f"INSERT INTO booking_rag_metadata ({cols_q}) VALUES ({placeholders})"
                    # print(query)
                    cursor.execute(query,values)
            connection.commit()
        # print(metadata)

    def delete_all(self) -> None:
        """
        Description:
            Method to delete all metadata from the database
        """       
        connection = self._create_connection()
        with connection:
            with connection.cursor() as cursor:
                query = f"TRUNCATE TABLE booking_rag_metadata;"
                cursor.execute(query)
            connection.commit()  

    def write_booking_details(self,booking_details:dict) -> None | dict:
        """
        Description:
            Method to write interview booking details to the database
        Arguments:
            booking_details = dict of booking fields
        """
        connection = self._create_connection()
        with connection:
            with connection.cursor() as cursor:
                # checking if the an interview is already booked for the given email
                email = booking_details['email']
                cursor.execute(f"SELECT * FROM booking_details WHERE email=%s",(email,))
                if cursor.rowcount > 0:
                    return {"Message":"An interview is already booked for this email"}

                cols = list(booking_details.keys())
                values = tuple(booking_details.values())
                cols_q = ", ".join(cols)
                placeholders = ", ".join(['%s']*len(cols))
                # print(cols)
                # print(values)
                query = f"INSERT INTO booking_details ({cols_q}) VALUES ({placeholders})"
                # print(query)
                cursor.execute(query,values)
            connection.commit()
        # print(metadata)


class VectorStore:
    def __init__(self):
        """
        Description:
            Constructor to initialize vector database credentials
        """
        self.PINECONE_API_KEY = os.getenv("PINECONE_API_KEY") # access variables
        self.PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
        self.PINECONE_HOST = os.getenv("PINECONE_HOST")
        self.pinecone_index = self.create_connection()
        
    def create_connection(self) -> pinecone.Pinecone:
        """
        Description:
            Method to create connection with vector database
        Return:
            Pinecone Index object
        """
        try:
            pc = pinecone.Pinecone(
            api_key=self.PINECONE_API_KEY
        )
            pinecone_index = pc.Index(host=self.PINECONE_HOST)
            return pinecone_index
        except Exception as e :
            raise Exception(f"Error creating connection with vector database : {str(e)}")
        
    def store(self,embeddings:np.array,texts:list,chunk_metadata:list)->None:
        """
        Description:
            Method to store embeddings,texts in vector database and metadata in sql database
        Arguments:
            embeddings: embedding vectors
            texts: corresponding texts of embedding vectors
            chunk_metadata : metadata of corresponding vectors
        """

        vectors = []
        metadata  = []
        for i, embedding in enumerate(embeddings): # enumerate() lets you loop over items and get their index at the same time.
            doc_id = f"doc_{uuid.uuid4().hex[:8]}_{i}"
            vectors.append(
               {
                "id": doc_id,
                "values": embedding.tolist(),
                "metadata": {"text": texts[i]}
                } 
            )
            metadata.append(
                {
                "id": doc_id,
                "uploaded_time": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "source": chunk_metadata[i]['source'] 
                }
            )  
        try:
            print("writting the metadata in the database")
            metadatadb = Metadata()
            metadatadb.delete_all() # delete metadata
            metadatadb.write(metadata=metadata)

            print("writting the vectors in the vectorstore")
            self.pinecone_index.delete(delete_all=True) # truncate vector database before adding vectors
            self.pinecone_index.upsert(vectors=vectors)
        except Exception as e:
            raise Exception(f"{str(e)}")

    def empty_index(self):
        """
        Description:
            Method to truncate the vector database
        """
        self.pinecone_index.delete(delete_all=True)
        print("PineCone index is emptied")


# if __name__ == "__main__":
#     chunk_obj = Chunk()
#     chunks = chunk_obj.create_chunk("recursive")
#     texts,metadata = chunk_obj.get_text_metadata(chunks=chunks)
#     embedding_manager = EmbeddingManager()
#     embeddings = embedding_manager.generate_embeddings(texts= texts)
#     store = VectorStore()
#     store.store(embeddings=embeddings,texts=texts,chunk_metadata=metadata)
