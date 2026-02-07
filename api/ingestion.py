from pathlib import Path
from fastapi import FastAPI, File, UploadFile
import shutil, os
from services.chunking import Chunk
from services.embedding import EmbeddingManager
from services.vectorstore import VectorStore

app = FastAPI()

# api for data ingestion
@app.post("/uploadfile/")
def upload_file(chunk_strategy:str,file: UploadFile = File(...)):
    # Save file locally
    try:
        file_name = Path(file.filename)
        supported_filetype = [".pdf",".txt"]
        if file_name.suffix in supported_filetype:
            DIR = f"data/booking_files"
            os.makedirs(DIR,exist_ok=True)
            with open(os.path.join(DIR,file.filename), "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            print("Uploaded files saved")
        else:
            raise Exception(f"File type not supported")

        chunk_obj = Chunk()
        chunks = chunk_obj.create_chunk(strategy= chunk_strategy)
        print("Chunking completed")

        texts,metadata = chunk_obj.get_text_metadata(chunks=chunks)
        embedding_manager = EmbeddingManager()
        embeddings = embedding_manager.generate_embeddings(texts= texts)

        store = VectorStore()
        store.store(embeddings=embeddings,texts=texts,chunk_metadata=metadata)
        print("Embeddings saved to vector store and metadata as well to sql db")
        
    except Exception as e:
        return {"Success": False,"error":str(e)} 
    return {"Success": True}