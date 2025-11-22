import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import AzureSearch
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import logging

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        self.vector_store = AzureSearch(
            azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
            azure_search_key=os.getenv("AZURE_SEARCH_KEY"),
            index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
            embedding_function=self.embeddings.embed_query
        )
        
        # Initialize Azure OpenAI if credentials exist
        try:
            self.llm = AzureChatOpenAI(
                azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                temperature=0
            )
            logger.info("RAG Service initialized with Azure AI Search and Azure OpenAI.")
        except Exception as e:
            self.llm = None
            logger.warning(f"Azure OpenAI not configured properly: {e}")

    def retrieve(self, query: str, k: int = 1) -> list:
        """
        Retrieve relevant documents from the knowledge base.
        """
        try:
            # Perform similarity search
            docs = self.vector_store.similarity_search(query, k=k)
            return [doc.page_content for doc in docs]
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []

    def generate_answer(self, query: str, context: list) -> str:
        """
        Generate an answer using an LLM.
        """
        if not context:
            return "I couldn't find any relevant medical guidelines in the knowledge base to answer your question."
            
        if not self.llm:
            # Fallback if LLM is not configured
            context_str = "\n\n".join(context[:2])
            return (
                f"**Based on the medical knowledge base, here is some relevant information:**\n\n"
                f"{context_str}\n\n"
                f"*(Note: Azure OpenAI credentials are required to generate a synthesized answer. "
                f"Currently showing raw retrieval results.)*"
            )

        # Prepare the prompt
        context_str = "\n\n".join(context)
        
        system_prompt = """You are a clinical assistant. Use the provided context to answer the doctor's question accurately.
        If the answer is not in the context, say you don't know. Keep answers concise."""
        
        user_prompt = f"Context:\n{context_str}\n\nQuestion: {query}"
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return "I encountered an error while generating the answer. Please check system logs."

    def process_query(self, query: str) -> dict:
        """
        End-to-end RAG pipeline: Retrieve -> Generate
        """
        context = self.retrieve(query)
        answer = self.generate_answer(query, context)
        return {
            "response": answer,
            "source_documents": context
        }