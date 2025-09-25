import sys
from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient
import pandas as pd
from difflib import get_close_matches

model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect to ChromaDB
chroma_client = PersistentClient(path="src/chroma_db")
collection = chroma_client.get_or_create_collection(name="dramas")

#Use Case 2: Prompt-based recommendation
def recommend_from_prompt(prompt: str, top_k: int = 5):
    embedding = model.encode(prompt)
    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k
    )

    print("\n Recommendations based on your prompt:\n")
    for doc in results['metadatas'][0]:
        print(f"🎬 {doc['title']} ({doc['country']}) — ⭐ {doc['rating']}")
        print(f"   ➤ https://mydramalist.com{doc['id']}\n")

#Use Case 3: Similar to a given drama title
def recommend_similar_drama(drama_title: str, top_k: int = 5):
    #We embed the input title (could be a nickname, alt title, etc.)
    query_embedding = model.encode(drama_title)

    #We find the closest match in the collection
    initial_result = collection.query(
        query_embeddings=[query_embedding],
        n_results=1,
        include=["metadatas", "embeddings"]
    )

    if not initial_result['metadatas'][0]:
        print("Drama not found in the collection.")
        return

    best_match = initial_result['metadatas'][0][0]
    best_title = best_match["title"]
    print(f"Using semantically closest drama: {best_title}")

    #We use its embedding to find similar dramas
    base_embedding = initial_result['embeddings'][0]

    similar_results = collection.query(
        query_embeddings=[base_embedding],
        n_results=top_k + 1,
        include=["metadatas", "distances"]
    )

    print(f"\nRecommendations similar to '{best_title}':\n")
    count = 0
    for doc in similar_results['metadatas'][0]:
        if doc['title'].lower() != best_title.lower():
            print(f"🎬 {doc['title']} ({doc['country']}) — ⭐ {doc['rating']}")
            print(f"   ➤ https://mydramalist.com{doc['id']}\n")
            count += 1
        if count >= top_k:
            break

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python recommend.py prompt \"your prompt here\"")
        print("  python recommend.py similar \"Drama Title\"")
        sys.exit(1)

    mode = sys.argv[1]
    input_text = " ".join(sys.argv[2:])

    if mode == "prompt":
        recommend_from_prompt(input_text)
    elif mode == "similar":
        recommend_similar_drama(input_text)
    else:
        print("Unknown mode. Use 'prompt' or 'similar'.")