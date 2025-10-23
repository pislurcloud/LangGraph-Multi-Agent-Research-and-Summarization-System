"""
Vector Store Setup using ChromaDB
"""
import os
from typing import List, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader

class VectorStoreManager:
    """Manages ChromaDB vector store for RAG"""
    
    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        collection_name: str = "technova_financial_docs",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        """
        Initialize Vector Store Manager
        
        Args:
            persist_directory: Directory to persist the vector store
            collection_name: Name of the Chroma collection
            embedding_model: HuggingFace model for embeddings
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Create persist directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        self.vectorstore: Optional[Chroma] = None
    
    def load_documents(self, data_path: str) -> List:
        """
        Load documents from directory
        
        Args:
            data_path: Path to directory containing documents
        
        Returns:
            List of loaded documents
        """
        print(f"Loading documents from {data_path}...")
        
        if not os.path.exists(data_path):
            raise ValueError(f"Data path does not exist: {data_path}")
        
        # Check if directory has files
        txt_files = list(Path(data_path).glob("**/*.txt"))
        if not txt_files:
            raise ValueError(f"No .txt files found in {data_path}")
        
        print(f"Found {len(txt_files)} .txt files")
        
        # Load text files with explicit encoding
        try:
            loader = DirectoryLoader(
                data_path,
                glob="**/*.txt",
                loader_cls=TextLoader,
                loader_kwargs={"encoding": "utf-8"},
                show_progress=True
            )
            documents = loader.load()
        except Exception as e:
            print(f"Error with utf-8 encoding, trying with default encoding: {e}")
            # Fallback to default encoding
            loader = DirectoryLoader(
                data_path,
                glob="**/*.txt",
                loader_cls=TextLoader,
                show_progress=True
            )
            documents = loader.load()
        
        if not documents:
            raise ValueError(f"No documents were loaded from {data_path}")
        
        print(f"✓ Loaded {len(documents)} documents")
        return documents
    
    def split_documents(self, documents: List, chunk_size: int = 1000, chunk_overlap: int = 200) -> List:
        """
        Split documents into chunks
        
        Args:
            documents: List of documents to split
            chunk_size: Size of each chunk
            chunk_overlap: Overlap between chunks
        
        Returns:
            List of document chunks
        """
        if not documents:
            raise ValueError("No documents provided to split")
        
        print("Splitting documents into chunks...")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        chunks = text_splitter.split_documents(documents)
        
        if not chunks:
            raise ValueError("Document splitting produced no chunks")
        
        print(f"✓ Created {len(chunks)} chunks")
        
        return chunks
    
    def create_vectorstore(self, documents: List):
        """
        Create vector store from documents
        
        Args:
            documents: List of documents to index
        """
        if not documents:
            raise ValueError("No documents provided to create vector store")
        
        print("Creating vector store...")
        
        try:
            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                collection_name=self.collection_name,
                persist_directory=self.persist_directory
            )
            
            print(f"✓ Vector store created with {len(documents)} documents")
            print(f"✓ Persisted to {self.persist_directory}")
        except Exception as e:
            raise Exception(f"Failed to create vector store: {str(e)}")
    
    def load_existing_vectorstore(self):
        """Load existing vector store from disk"""
        print("Loading existing vector store...")
        
        self.vectorstore = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )
        
        print("✓ Vector store loaded successfully")
    
    def similarity_search(self, query: str, k: int = 3) -> List:
        """
        Perform similarity search
        
        Args:
            query: Query string
            k: Number of results to return
        
        Returns:
            List of relevant documents
        """
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized. Call create_vectorstore() or load_existing_vectorstore() first.")
        
        results = self.vectorstore.similarity_search(query, k=k)
        return results
    
    def similarity_search_with_score(self, query: str, k: int = 3) -> List:
        """
        Perform similarity search with relevance scores
        
        Args:
            query: Query string
            k: Number of results to return
        
        Returns:
            List of (document, score) tuples
        """
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized.")
        
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        return results
    
    def get_retriever(self, k: int = 3):
        """
        Get retriever for RAG
        
        Args:
            k: Number of documents to retrieve
        
        Returns:
            Retriever instance
        """
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized.")
        
        return self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )

def initialize_vectorstore(
    data_path: str,
    persist_directory: str = "./chroma_db",
    force_recreate: bool = False
) -> VectorStoreManager:
    """
    Initialize or load vector store
    
    Args:
        data_path: Path to documents directory
        persist_directory: Directory to persist vector store
        force_recreate: Force recreation of vector store
    
    Returns:
        VectorStoreManager instance
    """
    manager = VectorStoreManager(persist_directory=persist_directory)
    
    # Check if vector store already exists
    vectorstore_exists = os.path.exists(persist_directory) and os.listdir(persist_directory)
    
    if vectorstore_exists and not force_recreate:
        print("📂 Found existing vector store")
        manager.load_existing_vectorstore()
    else:
        print("🆕 Creating new vector store")
        documents = manager.load_documents(data_path)
        chunks = manager.split_documents(documents)
        manager.create_vectorstore(chunks)
    
    return manager

if __name__ == "__main__":
    # Test vector store initialization
    import sys
    
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "financial_reports")
    
    try:
        manager = initialize_vectorstore(data_path, force_recreate=True)
        
        # Test similarity search
        query = "What was TechNova's revenue in Q1 2024?"
        results = manager.similarity_search(query, k=2)
        
        print(f"\n🔍 Test Query: {query}")
        print(f"Found {len(results)} relevant documents:\n")
        
        for i, doc in enumerate(results, 1):
            print(f"--- Result {i} ---")
            print(doc.page_content[:200] + "...")
            print()
        
        print("✅ Vector store test successful!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)