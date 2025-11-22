import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import AzureSearch

# Add src to path
sys.path.append(str(Path(__file__).resolve().parents[2]))

# Load env
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

def test_retrieval():
    print("Initializing Vector Store...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    vector_store = AzureSearch(
        azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
        azure_search_key=os.getenv("AZURE_SEARCH_KEY"),
        index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
        embedding_function=embeddings.embed_query
    )

    query = "classifications of pneumonia"
    print(f"\nQuerying: '{query}' (k=1)...\n")
    
    docs = vector_store.similarity_search(query, k=1)
    
    for i, doc in enumerate(docs):
        print(f"--- Result {i+1} ---")
        content = doc.page_content
        # Print first 500 chars to identify the chunk
        print(content[:500] + "...")
        
        # Check for key terms
        has_cap = "Community-Acquired" in content
        has_hap = "Hospital-Acquired" in content
        has_vap = "Ventilator-Associated" in content
        has_asp = "Aspiration" in content
        
        print(f"\nContains: CAP={has_cap}, HAP={has_hap}, VAP={has_vap}, ASP={has_asp}")
        print("-" * 50)

if __name__ == "__main__":
    test_retrieval()