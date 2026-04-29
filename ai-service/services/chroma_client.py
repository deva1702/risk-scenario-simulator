import chromadb
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)


# Load model once at startup
model = SentenceTransformer("all-MiniLM-L6-v2")

# Init persistent ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_data")
collection = chroma_client.get_or_create_collection(name="risk_knowledge")

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks

def ingest_document(doc_id: str, text: str):
    try:
        chunks = chunk_text(text)
        for i, chunk in enumerate(chunks):
            embedding = model.encode(chunk).tolist()
            collection.add(
                documents=[chunk],
                embeddings=[embedding],
                ids=[f"{doc_id}_chunk_{i}"]
            )
        logger.info(f"Ingested {len(chunks)} chunks for {doc_id}")
    except Exception as e:
        logger.error(f"Ingest failed: {e}")

def query_knowledge(question: str, top_k: int = 3):
    try:
        embedding = model.encode(question).tolist()
        results = collection.query(
            query_embeddings=[embedding],
            n_results=top_k
        )
        return results["documents"][0]
    except Exception as e:
        logger.error(f"Query failed: {e}")
        return []