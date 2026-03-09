import os
import requests
from dotenv import load_dotenv
from django.conf import settings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_community.vectorstores import FAISS
# Load the secrets from the .env file right after imports
load_dotenv()

def process_document(file_path):
    try:
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        # Chunk size is strictly controlled to ensure we get good context
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vector_store = FAISS.from_documents(chunks, embeddings)
        index_path = os.path.join(settings.BASE_DIR, 'faiss_index')
        vector_store.save_local(index_path)
        return True, "Document processed successfully!"
    except Exception as e:
        return False, str(e)

def search_document(query):
    try:
        # 1. Retrieve Context
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        index_path = os.path.join(settings.BASE_DIR, 'faiss_index')
        
        vector_store = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
        results = vector_store.similarity_search(query, k=4) # Increased k to get more context
        context_text = "\n\n".join([doc.page_content for doc in results])
        
        # 2. API Key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "Error: GEMINI_API_KEY is not set in environment variables."
        
        # 3. Model URL
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        
        headers = {"Content-Type": "application/json"}
        
        # --- THE "HYBRID" PROMPT (This makes it smart) ---
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"""
                    You are an expert tutor and intelligent assistant. The user has uploaded a document, and here is the relevant context from it:
                    
                    --- CONTEXT FROM DOCUMENT ---
                    {context_text}
                    -----------------------------
                    
                    USER QUESTION: {query}
                    
                    INSTRUCTIONS:
                    1. **Priority:** Start by answering based on the Document Context above.
                    2. **Expand:** If the document mentions a concept (like "{query}") but does not explain it in detail, YOU MUST use your own internal knowledge to explain it fully.
                    3. **Clarity:** Clearly state what comes from the document. For example: "According to the document, this is part of Unit III. Generally, in data science, this concept means..."
                    4. **Formatting:** Use HTML tags strictly (<h3>, <b>, <ul>, <li>, <p>). Do not use Markdown.
                    
                    Answer (in HTML):
                    """
                }]
            }]
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Error {response.status_code}: {response.text}"
            
    except Exception as e:
        return f"Error: {str(e)}"