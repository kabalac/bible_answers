import json
import chromadb
from sentence_transformers import SentenceTransformer


# Load Bible data
with open("data/bible.json", "r", encoding="utf-8") as file:
    bible = json.load(file)


print(f"Loaded {len(bible)} Bible verses.")


# Load embedding model
print("Loading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

print("Embedding model loaded.")


# Create Chroma database
client = chromadb.PersistentClient(path="data/chroma_db")

collection = client.get_or_create_collection(
    name="bible_verses"
)


# Prepare data
documents = []
metadatas = []
ids = []

for index, verse in enumerate(bible):
    documents.append(verse["text"])

    metadatas.append({
        "book": verse["book"],
        "chapter": verse["chapter"],
        "verse": verse["verse"]
    })

    ids.append(str(index))


# Create embeddings
print("Creating embeddings...")

embeddings = model.encode(
    documents,
    show_progress_bar=True
)


# Store in Chroma
print("Saving verses to ChromaDB...")

BATCH_SIZE = 5000

for start in range(0, len(ids), BATCH_SIZE):
    end = start + BATCH_SIZE

    collection.add(
        ids=ids[start:end],
        documents=documents[start:end],
        metadatas=metadatas[start:end],
        embeddings=embeddings[start:end].tolist()
    )

    print(f"Saved verses {start + 1} to {min(end, len(ids))}")
    
print("\nBible vector database created successfully!")
print(f"Total verses indexed: {collection.count()}")