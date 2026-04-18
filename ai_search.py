import os
from langchain_community.document_loaders import Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaLLM  # <-- NEW UPDATED IMPORT
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# --- 1. INGEST & PARSE ---
print("📄 Loading Word Document...")
file_path = "Marketing Analytics - CAC Deep Dive Dashboard.docx"
loader = Docx2txtLoader(file_path)
documents = loader.load()

# --- 2. CHUNKING ---
print("✂️ Chunking text into processable pieces...")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # <-- WIDER CHUNKS (Keeps tables intact)
    chunk_overlap=200,    
    separators=["\n\n", "\n", " ", ""]
)
chunks = text_splitter.split_documents(documents)

# --- 3. EMBEDDING & VECTOR DATABASE ---
print("🧠 Building Vector Database...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

vector_db = Chroma.from_documents(
    documents=chunks, 
    embedding=embeddings, 
    persist_directory="./chroma_db" 
)

# --- 4. THE MODERN LLM ENGINE (LCEL) ---
print("🤖 Booting up Local LLM (LLaMA 3)...")
llm = OllamaLLM(model="llama3") # <-- NEW UPDATED CLASS

# The Instructions
prompt_template = ChatPromptTemplate.from_template("""
You are a helpful Data Governance Assistant. Answer the user's question based ONLY on the provided context. 
If the context contains tabular data, you MUST format your answer as a clean Markdown table.
Do not make up information. If the answer is not in the context, say "I don't know based on the documentation."

Context:
{context}

Question: {input}
""")

# The Retriever
retriever = vector_db.as_retriever(search_kwargs={"k": 6}) # <-- GRAB TOP 6 CHUNKS INSTEAD OF 3

# Helper function to merge the chunks into one readable string for the AI
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# The LCEL Pipeline
rag_chain = (
    {"context": retriever | format_docs, "input": RunnablePassthrough()}
    | prompt_template
    | llm
    | StrOutputParser()
)

# --- 5. THE NATURAL LANGUAGE SEARCH ---
print("="*50)
print("🤖 AI DOC SEARCH ENGINE READY")
print("="*50)

while True:
    query = input("\nAsk a question about the CAC Dashboard (or type 'exit'): ")
    if query.lower() == 'exit':
        break
    
    print("\n[AI is thinking...]")
    
    # Run the query through the pipeline
    response = rag_chain.invoke(query)
    
    # Print the beautifully formatted answer
    print("\n--- ANSWER ---")
    print(response)
    print("-" * 30)