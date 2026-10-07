import os
from pypdf import PdfReader
import chromadb
from google import genai
from app.config import settings
import json

# ChromaDB bağlantısı
CHROMA_DATA_PATH = "./data/chroma_db"
os.makedirs(CHROMA_DATA_PATH, exist_ok=True)
chroma_client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
collection = chroma_client.get_or_create_collection(name="docupulse_docs")

def get_ai_client():
    return genai.Client(api_key=settings.GEMINI_API_KEY)

def extract_and_chunk_pdf(file_path: str, chunk_size: int = 500, overlap: int = 50):
    reader = PdfReader(file_path)
    chunks = []
    
    for page_idx, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text = " ".join(text.split())
        if not text:
            continue
            
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]
            chunks.append({
                "page": page_idx + 1,
                "text": chunk_text
            })
            start += (chunk_size - overlap)
            
    return chunks

def index_pdf_file(user_id: int, doc_id: int, file_path: str, filename: str) -> int:
    chunks = extract_and_chunk_pdf(file_path)
    
    documents = []
    metadatas = []
    ids = []
    
    for i, c in enumerate(chunks):
        chunk_id = f"doc_{doc_id}_chunk_{i}"
        documents.append(c["text"])
        metadatas.append({
            "user_id": user_id,
            "document_id": doc_id,
            "filename": filename,
            "page": c["page"]
        })
        ids.append(chunk_id)
        
    if documents:
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    return len(chunks)

def query_rag_engine(user_id: int, query_text: str) -> dict:
    results = collection.query(
        query_texts=[query_text],
        n_results=4,
        where={"user_id": user_id}
    )
    
    retrieved_docs = results["documents"][0] if results.get("documents") and results["documents"] else []
    retrieved_metas = results["metadatas"][0] if results.get("metadatas") and results["metadatas"] else []
    
    if not retrieved_docs:
        return {
            "answer": "Sorguyla eşleşen yüklenmiş bir doküman içeriği bulunamadı.",
            "citations": []
        }
    
    context = ""
    citations = []
    for doc, meta in zip(retrieved_docs, retrieved_metas):
        citations.append({"filename": meta.get("filename", "Belge"), "page": meta.get("page", 1)})
        context += f"\n[Doküman: {meta.get('filename')} (Sayfa {meta.get('page')})]:\n{doc}\n"
    
    prompt = (
        f"Sen DocuPulse doküman asistanısın. Yalnızca aşağıdaki BAĞLAM bilgilerini kullanarak soruyu yanıtla. "
        f"Cevabında bilginin hangi doküman ve sayfadan alındığını belirt.\n\n"
        f"BAĞLAM:\n{context}\n\n"
        f"SORU:\n{query_text}"
    )
    
    client = get_ai_client()
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )
    
    return {
        "answer": response.text,
        "citations": citations
    }
    

def stream_rag_engine(user_id: int, query_text: str):
    # 1. Benzer doküman parçalarını getir
    results = collection.query(
        query_texts=[query_text],
        n_results=4,
        where={"user_id": user_id}
    )

    retrieved_docs = results["documents"][0] if results.get("documents") and results["documents"] else []
    retrieved_metas = results["metadatas"][0] if results.get("metadatas") and results["metadatas"] else []

    if not retrieved_docs:
        yield f"data: {json.dumps({'event': 'done', 'answer': 'No relevant document content found for this query.', 'citations': []})}\n\n"
        return

    context = ""
    citations = []
    for doc, meta in zip(retrieved_docs, retrieved_metas):
        citations.append({
            "filename": meta.get("filename", "Unknown"),
            "page": meta.get("page", 1)
        })
        context += f"\n[Document: {meta.get('filename')} (Page {meta.get('page')})]:\n{doc}\n"

    # İlk olarak kaynakçayı (citations) arayüze ilet
    yield f"data: {json.dumps({'event': 'citations', 'citations': citations})}\n\n"

    system_prompt = (
        "You are DocuPulse AI, an intelligent corporate document assistant. "
        "Answer the user query strictly using the provided CONTEXT below. "
        "Always cite your sources mentioning the document name and page number. "
        "If the information is not present in the context, clearly state that the provided documents do not contain the answer.\n\n"
        f"CONTEXT:\n{context}\n\n"
        f"USER QUERY:\n{query_text}"
    )

    client = get_ai_client()
    response_stream = client.models.generate_content_stream(
        model="gemini-3.5-flash",
        contents=system_prompt
    )

    # Yanıt parçalarını anlık olarak akıt
    for chunk in response_stream:
        if chunk.text:
            yield f"data: {json.dumps({'event': 'token', 'text': chunk.text})}\n\n"

    yield f"data: {json.dumps({'event': 'end'})}\n\n"