import os
import math
import re
from collections import Counter
from typing import List, Dict, Tuple, Any

from langchain.retrievers import EnsembleRetriever, BM25Retriever
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings

class ScratchBM25Retriever:
    def __init__(self, documents, k1=1.5, b=0.75, epsilon=0.25):
        self.k1 = k1
        self.b = b
        self.epsilon = epsilon
        self.k = 5  # Default number of documents to retrieve
        # Process and index documents
        self.documents = documents
        self.doc_contents = [doc.page_content for doc in documents]
        self.doc_lengths = [len(self._tokenize(content)) for content in self.doc_contents]
        self.avg_doc_length = sum(self.doc_lengths) / len(self.doc_lengths) if self.doc_lengths else 0
        # Build inverted index and document frequency counts
        self.inverted_index = self._build_inverted_index()
        self.N = len(documents)  # Total number of documents
        
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization: lowercase, remove punctuation, split on whitespace."""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        return text.split()
    
    def _build_inverted_index(self) -> Dict[str, Dict[int, int]]:
        """Build an inverted index mapping tokens to document IDs and term frequencies."""
        inverted_index = {}
        
        for doc_id, content in enumerate(self.doc_contents):
            tokens = self._tokenize(content)
            term_freq = Counter(tokens)
            
            for token, freq in term_freq.items():
                if token not in inverted_index:
                    inverted_index[token] = {}
                inverted_index[token][doc_id] = freq
        
        return inverted_index
    
    def _calculate_idf(self, token: str) -> float:
        """Calculate Inverse Document Frequency for a token."""
        # Number of documents containing the token
        doc_count = len(self.inverted_index.get(token, {}))
        
        # Smoothed IDF (add 1 to doc_count to avoid division by zero)
        idf = math.log((self.N - doc_count + 0.5) / (doc_count + 0.5) + 1.0)
        return max(self.epsilon, idf)  # Apply minimum threshold
    
    def _score_document(self, query_tokens: List[str], doc_id: int) -> float:
        """Calculate BM25 score for a document given query tokens."""
        score = 0.0
        doc_length = self.doc_lengths[doc_id]
        # Calculate length normalization factor
        length_norm = (1.0 - self.b) + self.b * (doc_length / self.avg_doc_length)
        
        for token in query_tokens:
            if token in self.inverted_index and doc_id in self.inverted_index[token]:
                # Term frequency in document
                tf = self.inverted_index[token][doc_id]
                # IDF score for token
                idf = self._calculate_idf(token)
                # BM25 formula for term's contribution to document score
                numerator = idf * tf * (self.k1 + 1)
                denominator = tf + self.k1 * length_norm
                score += numerator / denominator
        
        return score
    
    def get_relevant_documents(self, query: str) -> List[Any]:
        """Retrieve the most relevant documents for a query."""
        query_tokens = self._tokenize(query)
        
        # Score each document
        doc_scores = []
        for doc_id in range(self.N):
            score = self._score_document(query_tokens, doc_id)
            if score > 0:  # Only consider documents with non-zero scores
                doc_scores.append((doc_id, score))
        
        # Sort documents by score (descending) and take top k
        doc_scores.sort(key=lambda x: x[1], reverse=True)
        top_docs = [self.documents[doc_id] for doc_id, _ in doc_scores[:self.k]]
        
        return top_docs
    
    def set_k(self, k: int):
        """Set the number of documents to retrieve."""
        self.k = k

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
    """Set up and return ensemble and custom retrievers."""
    kb_retriever = vector_store.as_retriever(search_kwargs={"k": 5})  # Vector search
    
    # Use LangChain's built-in BM25Retriever
    langchain_bm25 = BM25Retriever.from_documents(chunks)
    langchain_bm25.k = 5
    
    # Create custom BM25 for separate use
    custom_bm25 = ScratchBM25Retriever(chunks, k1=1.5, b=0.75)
    custom_bm25.set_k(5)
    
    return EnsembleRetriever(retrievers=[kb_retriever, langchain_bm25], weights=[0.5, 0.5]), custom_bm25