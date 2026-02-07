## Embedding
import numpy as np
from  sentence_transformers import SentenceTransformer # this is our embedding model
from typing import List
from services.chunking import Chunk


class EmbeddingManager: 
    """
    handles document embedding generation using sentence transformer model
    """
    def __init__(self,model_name:str="all-MiniLM-L6-v2"): 
        """
        Constructor to initialize the EmbeddingManager
        Arguments:
            model_name = hugging face sentence transformer model name
        """
        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self) -> None:
        """
        Load the specified sentence transformer model
        """
        try:
            print(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            print(f"Loaded embedding model successfully. Embedding Dimensions = {self.model.get_sentence_embedding_dimension}")
        except Exception as  e:
            raise Exception(f"Error loading model{self.model_name} = {str(e)}")

    def generate_embeddings(self,texts:List[str]) -> np.array:
        """
        Generates embeddings for list of text
        Arguments:
            List of texts whose embedding is to be generated
        Return:
            numpy array with shape = (len(texts),embedding_dimensions)
        """
        if not self.model:
            raise ValueError("Model not loaded")
        print(f"Creating embeddings for {len(texts)} texts.")
        embeddings = self.model.encode(texts,show_progress_bar=True)
        print(f"Embeddings generated successfully with shape = {embeddings.shape}")
        return embeddings


# if __name__ == "__main__":
#     chunk_obj = Chunk()
#     chunks = chunk_obj.create_chunk("recursive")
#     texts,metadata = chunk_obj.get_text_metadata(chunks=chunks)
#     embedding_manager = EmbeddingManager()
#     embeddings = embedding_manager.generate_embeddings(texts= texts)
#     print(embeddings)
