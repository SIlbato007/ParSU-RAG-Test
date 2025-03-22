import os
from dotenv import load_dotenv
from src.data_processing import load_document, recursive_chunk
from src.retriever import create_embedding_model, create_vector_store, setup_retrievers
from src.llm import setup_llm, setup_prompt_template, assemble_chain
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load and set environment variables
load_dotenv()
HF_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

# Check if token exists
if not HF_TOKEN:
    logger.warning("HuggingFace API token not found in environment variables.")
else:
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = HF_TOKEN

class PSUChatBackend:
    def __init__(self, persist_directory="chroma_db"):
        """Initialize backend with a persistent directory for ChromaDB."""
        self.chain = None
        self.persist_directory = persist_directory
        self.chunks = None
        self.custom_bm25 = None  # Store custom BM25 for later use if needed
        self.vector_store = None
        self.is_initialized = False
        
        # Make sure the persist directory exists
        os.makedirs(self.persist_directory, exist_ok=True)

    def initialize_system(self, pdf_path="data/charter_data.pdf"):
        """Initialize the entire system, reusing stored embeddings if available."""
        try:
            logger.info("Initializing the system...")
            
            # Check if token exists
            if not HF_TOKEN:
                return False, "HuggingFace API token not found. Please set the HUGGINGFACEHUB_API_TOKEN environment variable."
            
            # Create embedding model
            embeddings = create_embedding_model(HF_TOKEN)
            
            # Check if the PDF file exists
            if not os.path.exists(pdf_path):
                return False, f"PDF file not found at {pdf_path}"

            # Check if ChromaDB exists; load or create as needed
            if os.path.exists(self.persist_directory) and os.listdir(self.persist_directory):
                logger.info("Using existing vector store from %s", self.persist_directory)
                self.vector_store = create_vector_store([], embeddings, self.persist_directory)
                
                # If we're loading a pre-existing vector store, we need to load the document chunks
                if not self.chunks:
                    logger.info("Loading document from %s", pdf_path)
                    data = load_document(pdf_path)
                    self.chunks = recursive_chunk(data)
            else:
                logger.info("Creating new vector store from document at %s", pdf_path)
                data = load_document(pdf_path)
                self.chunks = recursive_chunk(data)
                self.vector_store = create_vector_store(self.chunks, embeddings, self.persist_directory)

            # Setup retrievers - get both the ensemble retriever and the custom one
            logger.info("Setting up retrievers...")
            ensemble_retriever, self.custom_bm25 = setup_retrievers(self.vector_store, self.chunks)

            # Setup LLM and prompt chain components
            logger.info("Setting up LLM and prompt chain...")
            llm = setup_llm()
            prompt, output_parser = setup_prompt_template()
            self.chain = assemble_chain(ensemble_retriever, prompt, llm, output_parser)
            
            self.is_initialized = True
            logger.info("System initialized successfully!")
            return True, "System initialized successfully!"
        except Exception as e:
            logger.error("Error during initialization: %s", str(e), exc_info=True)
            return False, f"Error during initialization: {str(e)}"
    
    def generate_response(self, query):
        """Generate a response for the given query."""
        if not self.chain:
            logger.warning("Attempt to generate response with uninitialized system")
            return False, "System not initialized. Please initialize first."
        
        try:
            logger.info("Generating response for query: %s", query)
            response = self.chain.invoke(query)
            logger.info("Response generated successfully")
            return True, response
        except Exception as e:
            logger.error("Error generating response: %s", str(e), exc_info=True)
            return False, f"Error generating response: {str(e)}"
            
    def get_custom_bm25_results(self, query, k=5):
        """Separate method to directly use the custom BM25 implementation."""
        if not self.custom_bm25:
            logger.warning("Attempt to use custom BM25 when it's not initialized")
            return False, "Custom BM25 not initialized."
        
        try:
            logger.info("Retrieving BM25 results for query: %s (k=%d)", query, k)
            self.custom_bm25.set_k(k)
            results = self.custom_bm25.get_relevant_documents(query)
            return True, results
        except Exception as e:
            logger.error("Error retrieving BM25 results: %s", str(e), exc_info=True)
            return False, f"Error retrieving results: {str(e)}"