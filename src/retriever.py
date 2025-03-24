import os
from langchain.retrievers import EnsembleRetriever, BM25Retriever
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings

def create_embedding_model(api_key, model_name="BAAI/bge-base-en-v1.5"):
    """Create an embedding model instance."""
    return HuggingFaceInferenceAPIEmbeddings(api_key=api_key, model_name=model_name)

def create_vector_store(chunks, embeddings, persist_directory):
    """Create or load a Chroma vector store."""
    if os.path.exists(persist_directory) and os.listdir(persist_directory):
        return Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    
    return Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory
    )

def setup_retrievers(vector_store, chunks):
    """Set up and return ensemble retriever using vector search and langchain's BM25."""
    kb_retriever = vector_store.as_retriever(search_kwargs={"k": 5})  # Vector search
    # BM25
    bm25 = BM25Retriever.from_documents(chunks)
    bm25.k = 5
    # Create ensemble with both retrievers
    ensemble = EnsembleRetriever(
        retrievers=[kb_retriever, bm25], 
        weights=[0.5, 0.5]
    )
    
    return ensemble
