from langchain.document_loaders import UnstructuredPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def load_document(pdf_path):
    """Load a PDF document using UnstructuredPDFLoader."""
    loader = UnstructuredPDFLoader(pdf_path)
    return loader.load()

def recursive_chunk(data, chunk_size=512, chunk_overlap=100):
    """Split loaded document into chunks using RecursiveCharacterTextSplitter."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_documents(data)
