from langchain_community.document_loaders import PyPDFLoader
import os

# Target file
pdf_path = "clinical-intelligence-platform/data/2_generative_data/knowledge_base/Pneumonia_ In-Depth Medical Report_.pdf"

def debug_pdf():
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return

    print(f"--- Extracting text from: {os.path.basename(pdf_path)} ---")
    try:
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()
        
        if not pages:
            print("No pages extracted.")
            return

        # Print the first 2000 characters of the first few pages to inspect quality
        full_text = ""
        for page in pages[:3]: # Check first 3 pages
            full_text += page.page_content + "\n\n"
            
        print(full_text[:3000]) # Print first 3000 chars

    except Exception as e:
        print(f"Error reading PDF: {e}")

if __name__ == "__main__":
    debug_pdf()