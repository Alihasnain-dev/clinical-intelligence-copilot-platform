import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import AzureSearch
from azure.storage.blob import BlobServiceClient
import uuid
import json
# from azure.identity import DefaultAzureCredential # Removed in favor of SAS Token
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(dotenv_path=str(PROJECT_ROOT / ".env"), override=True)

# Azure configuration
STORAGE_ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME", "clinicaldatalake25")
KNOWLEDGE_BASE_CONTAINER_NAME = os.getenv("KNOWLEDGE_BASE_CONTAINER_NAME", "knowledge-base")
SAS_TOKEN = os.getenv("SAS_TOKEN")

# Azure AI Search configuration
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT", "https://clinical-ai-search-service-2025.search.windows.net")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME", "clinical-knowledge-index-v2")

# Embedding model configuration
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
BATCH_SIZE = 4  # Smaller batches avoid Search API size limits

def require(value: str, name: str) -> str:
    """Ensures required configuration values exist before running the pipeline."""
    if not value:
        raise ValueError(f"Environment variable '{name}' is not set.")
    return value


def download_pdfs_from_blob():
    """Downloads all PDFs from blob storage to a local temporary directory."""
    local_pdf_dir = "temp_pdfs"
    os.makedirs(local_pdf_dir, exist_ok=True)
    
    print("Connecting to Blob Storage...")
    storage_account = require(STORAGE_ACCOUNT_NAME, "STORAGE_ACCOUNT_NAME")
    sas_token = require(SAS_TOKEN, "SAS_TOKEN")
    
    # Determine if SAS token already has the leading '?' or not
    if not sas_token.startswith("?"):
        sas_token = f"?{sas_token}"

    storage_account_url = f"https://{storage_account}.blob.core.windows.net"
    # Use SAS Token for authentication
    blob_service_client = BlobServiceClient(account_url=storage_account_url, credential=sas_token)
    container_client = blob_service_client.get_container_client(KNOWLEDGE_BASE_CONTAINER_NAME)

    print(f"Downloading PDFs from container '{KNOWLEDGE_BASE_CONTAINER_NAME}'...")
    blob_list = container_client.list_blobs()
    downloaded_files = []
    for blob in blob_list:
        if blob.name.lower().endswith(".pdf"):
            local_file_path = os.path.join(local_pdf_dir, os.path.basename(blob.name))
            with open(local_file_path, "wb") as download_file:
                download_file.write(container_client.download_blob(blob.name).readall())
            downloaded_files.append(local_file_path)
            print(f"  Downloaded: {blob.name}")
    return downloaded_files, local_pdf_dir

def main():
    """
    Main function to build and populate the Azure AI Search vector index.
    """
    # 1. Download PDFs from Blob Storage
    pdf_files, pdf_dir = download_pdfs_from_blob()
    if not pdf_files:
        print("No PDF files found. Exiting.")
        return

    # 2. Load and Chunk Documents
    print("\nLoading and chunking documents...")
    all_docs = []
    for pdf_file in pdf_files:
        loader = PyPDFLoader(pdf_file)
        documents = loader.load()
        
        # CLEANING STEP: Remove excessive whitespace
        import re
        for doc in documents:
            content = doc.page_content
            # Regex to replace all whitespace (newlines, tabs, spaces) sequences with a single space
            cleaned_content = re.sub(r'\s+', ' ', content).strip()
            doc.page_content = cleaned_content
            
        all_docs.extend(documents)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2200, chunk_overlap=500)
    chunked_docs = text_splitter.split_documents(all_docs)
    print(f"Total documents chunked into {len(chunked_docs)} pieces.")

    # Sanitize metadata to ensure all values are primitive types
    def sanitize_metadata(data):
        """Recursively sanitizes metadata to ensure all values are primitive types."""
        if isinstance(data, dict):
            return {k: sanitize_metadata(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [sanitize_metadata(i) for i in data]
        elif not isinstance(data, (str, int, float, bool, type(None))):
            return str(data)
        return data

    for doc in chunked_docs:
        doc.metadata = sanitize_metadata(doc.metadata)

    # 3. Create Embeddings
    print(f"\nInitializing embedding model: '{EMBEDDING_MODEL_NAME}'...")
    # This will download the model from Hugging Face the first time you run it
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    print("Embedding model loaded.")

    # 4. Initialize and Populate Azure AI Search Vector Store
    print(f"\nPopulating Azure AI Search index '{INDEX_NAME}' in batches of {BATCH_SIZE} chunks...")
    azure_search_key = require(AZURE_SEARCH_KEY, "AZURE_SEARCH_KEY")
    # Define Azure AI Search index schema
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="content", type=SearchFieldDataType.String, searchable=True),
        SearchField(name="content_vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                      searchable=True, vector_search_dimensions=384, vector_search_profile_name="my-hnsw-profile"),
        SearchableField(name="metadata", type=SearchFieldDataType.String, searchable=True),
        SearchableField(name="source", type=SearchFieldDataType.String, filterable=True),
        SearchableField(name="page", type=SearchFieldDataType.String, filterable=True),
    ]

    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name="my-hnsw-vector-config")],
        profiles=[VectorSearchProfile(name="my-hnsw-profile", algorithm_configuration_name="my-hnsw-vector-config")]
    )

    index = SearchIndex(name=INDEX_NAME, fields=fields, vector_search=vector_search)
    
    # Create or update the index
    print(f"Creating or updating index '{INDEX_NAME}'...")
    credential = AzureKeyCredential(azure_search_key)
    index_client = SearchIndexClient(endpoint=AZURE_SEARCH_ENDPOINT, credential=credential)
    
    # DELETE EXISTING INDEX to ensure we don't have duplicate dirty data
    try:
        print(f"Deleting existing index '{INDEX_NAME}' to ensure clean slate...")
        index_client.delete_index(INDEX_NAME)
        print("Index deleted.")
    except Exception:
        print("Index did not exist or could not be deleted.")

    index_client.create_or_update_index(index)
    print("Index created successfully.")

    vector_store = AzureSearch(
        azure_search_endpoint=AZURE_SEARCH_ENDPOINT,
        azure_search_key=azure_search_key,
        index_name=INDEX_NAME,
        embedding_function=embeddings.embed_documents
    )
    
    # 5. Manually prepare and upload data in batches
    total_chunks = len(chunked_docs)
    for start in range(0, total_chunks, BATCH_SIZE):
        end = min(start + BATCH_SIZE, total_chunks)
        batch = chunked_docs[start:end]

        # Generate embeddings for the entire batch in one call to avoid repeated model invocations
        batch_contents = [doc.page_content for doc in batch]
        batch_embeddings = embeddings.embed_documents(batch_contents)

        # Manually create the payload for Azure AI Search
        documents_to_upload = []
        for doc, content_vector in zip(batch, batch_embeddings):
            documents_to_upload.append({
                "id": str(uuid.uuid4()),
                "content": doc.page_content,
                "content_vector": content_vector,
                "metadata": json.dumps(sanitize_metadata(doc.metadata)),
                "source": doc.metadata.get("source", ""),
                "page": str(doc.metadata.get("page", ""))
            })

        print(f"  -> Uploading chunks {start + 1}-{end} of {total_chunks}...")
        search_client = vector_store.client
        search_client.upload_documents(documents=documents_to_upload)

    print("\n-------------------------------------")
    print("Vector index build process completed successfully!")
    print("Your knowledge base is now indexed and searchable.")
    print("-------------------------------------")
    
    # Optional: Clean up downloaded files
    # for pdf in pdf_files:
    #     os.remove(pdf)
    # os.rmdir(pdf_dir)

if __name__ == "__main__":
    main()
