import pymupdf as fitz
from collections import Counter
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb
def data_extract():
    doc = fitz.open("data/fia_2026_f1_regulations_section_b_sporting.pdf")
    text =""
    for page in doc:
        text +=page.get_text()
    return text

def clean_text(text):
    lines = text.split("\n")
    count = Counter(lines)
    cleaned_lines = [line for line in lines if count[line] <= 85]
    return "\n".join(cleaned_lines)

def chunk_text(txt):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size= 600, chunk_overlap= 80)
    return text_splitter.split_text(txt)

def embed_text(chunks):
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    embeddings = model.encode(chunks,  normalize_embeddings=True)
    return embeddings

client= chromadb.PersistentClient("./chromadb")
collection = client.get_or_create_collection(name="the_stewards_room", metadata={"hnsw:space": "cosine"})
def ingest_db(embeddings,chunks):
    embeddings = embeddings.tolist()
    chunk_id =[]
    metadata=[]
    for i in range(1, len(chunks)+1):
        chunk_id.append(f"chunk_{i}")
        temp = {"source":"fia_2026_f1_regulations_section_b_sporting.pdf", "doc_type":"sporting"}
        metadata.append(temp)
    collection.add(
        ids= chunk_id,
        embeddings= embeddings,
        metadatas= metadata,
        documents= chunks
    )
    return collection.count()

if __name__ == "__main__":
    data = data_extract()
    cleaned = clean_text(data)
    chunks = chunk_text(cleaned)
    embeds = embed_text(chunks)
    ingestor = ingest_db(embeds, chunks)
    print(ingestor)