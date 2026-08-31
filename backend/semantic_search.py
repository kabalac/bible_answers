import chromadb
from sentence_transformers import SentenceTransformer


# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


# Connect to our existing ChromaDB
client = chromadb.PersistentClient(path="data/chroma_db")

collection = client.get_collection(
    name="bible_verses"
)


# Get user's feeling
feeling = input("How are you feeling? ")


# Convert feeling into an embedding
query_embedding = model.encode([feeling])[0].tolist()


# Search for semantically similar verses
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=5,
    include=["documents", "metadatas", "distances"]
)

print("\nRelevant Bible verses:\n")


for document, metadata, distance in zip(
    results["documents"][0],
    results["metadatas"][0],
    results["distances"][0]
):
    print(
        f'{metadata["book"]} '
        f'{metadata["chapter"]}:{metadata["verse"]}\n'
        f'Similarity distance: {distance:.4f}\n'
        f'{document}\n'
    )