from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader, TextLoader
# import os

class Chunk:
    def __init__(self):
        self.doc_dir = f"data/booking_files"
        
    def create_chunk(self,strategy:str) -> list[Document] | str:# the type annotations doesnot force to be followed
        """
        Description:
            Chunking based on user preference
        Arguments:
            strategy: name of the chunking strategy. Supported strategies = "document","recursive"
        Return:
            list of documents/chunks or, string
        """
        if strategy == "document":
            # document chunking method
            pdf_loader = DirectoryLoader(
                                    self.doc_dir,
                                    glob="**/*.pdf", # filename pattern 
                                    loader_cls=PyMuPDFLoader, # loader class to use
                                    )
            docs = pdf_loader.load()
            txt_loader = DirectoryLoader(
                                    self.doc_dir,
                                    glob="**/*.txt", # filename pattern 
                                    loader_kwargs={"encoding": "utf-8"},
                                    loader_cls=TextLoader, # loader class to use
                                    )
            docs.extend(txt_loader.load())
            
            print(f"Chunks created: {len(docs)}")
            return docs

        elif strategy == "recursive":
            # recursive character chunking method
            pdf_loader = DirectoryLoader(
                                    self.doc_dir,
                                    glob="**/*.pdf", # filename pattern 
                                    loader_cls=PyMuPDFLoader, # loader class to use
                                    )
            docs = pdf_loader.load()
            txt_loader = DirectoryLoader(
                                    self.doc_dir,
                                    glob="**/*.txt", # filename pattern 
                                    loader_kwargs={"encoding": "utf-8"},
                                    loader_cls=TextLoader, # loader class to use
                                    )
            docs.extend(txt_loader.load())
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,        # characters per chunk
                chunk_overlap=200,      # overlap to preserve context
                separators=["\n\n", "\n", " ", ""]
            )

            chunks = text_splitter.split_documents(docs)
            print(f"Chunks created: {len(chunks)}")
            return chunks
    
        else:
            # return f"chunking strategy not supported!!!!"
            raise Exception(f"{strategy} chunking strategy not supported!!!!")

    def get_text_metadata(self,chunks:list[Document]) -> tuple:
        """
        Docstring for get_text_metadata
        
        Arguments:
            chunks: list of documents/chunks
        Return: 
            tuple of texts(list) and chunk's metadata(list)
        """
        texts = []
        chunk_metadata = []
        for chunk in chunks:
            texts.append(chunk.page_content)
            chunk_metadata.append(chunk.metadata)
        # print(len(texts))
        # print(texts)
        chunk_metadata = [chunk.metadata  for chunk in chunks]
        # print(len(chunk_metadata))
        # print(chunk_metadata)
        return (texts,chunk_metadata)

# if __name__ == "__main__":
#     chunks = Chunk().create_chunk(strategy="recursive") 
#     print(len(chunks))
#     for each in chunks:
#         print(each,"\n\n")