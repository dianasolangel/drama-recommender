import sys
from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient
import pandas as pd
import ast # for safely evaluating strings of lists

model = SentenceTransformer("all-MiniLM-L6-v2") 

#Connection to ChromaDB
chroma_client = PersistentClient(path="src/chroma_db")
collection = chroma_client.get_or_create_collection(name="dramas")

"""Prompt-based recommendation"""

def recommend_from_prompt(prompt: str, top_k: int = 5, return_streamlit: bool = False):
    embedding = model.encode(prompt)
    results = collection.query(query_embeddings=[embedding], n_results=top_k)

    dramas = []
    for doc in results['metadatas'][0]:
        title = doc.get("title", "Unknown Title")
        country = doc.get("country", "Unknown Country")
        rating = doc.get("rating", "N/A")
        url = doc.get("url", f"https://mydramalist.com/{doc.get('id', '')}")
        # genres = ", ".join(ast.literal_eval(doc.get("genres", "[]"))) if isinstance(doc.get("genres"), str) else ""
        raw_genres = doc.get("genres", "[]")

        try:
            # Vérifie que c'est une chaîne qui ressemble à une liste avant d'utiliser literal_eval
            if isinstance(raw_genres, str) and raw_genres.strip().startswith("["):
                genres_list = ast.literal_eval(raw_genres)
                genres = ", ".join(genres_list)
            else:
                genres = raw_genres if isinstance(raw_genres, str) else ""
        except (ValueError, SyntaxError):
            genres = ""
        tags = ", ".join(doc.get("tags", [])) if isinstance(doc.get("tags"), list) else ""

        dramas.append({
            "title": title,
            "country": country,
            "rating": rating,
            "url": url,
            "genres": genres,
            "tags": tags
        })

        if not return_streamlit:
            print(f"{title} ({country}) — ⭐{rating}")
            if genres:
                print(f"Genres: {genres}")
            if tags:
                print(f"Tags: {tags}")
            print(f"  ➤ {url}\n")

    if return_streamlit:
        return dramas
        
        
"Recommendation based on a similar already watched drama"
def recommend_similar_drama(drama_title: str, top_k: int = 5, min_rating: float = 8.0, return_streamlit: bool = False):
    
    # To find the reference drama in the collection
    query_embedding = model.encode(drama_title)
    initial_result = collection.query(
        query_embeddings=[query_embedding],
        n_results=1,
        include=["metadatas", "embeddings"])

    if not initial_result['metadatas'][0]:
        print("Drama not found in the collection.")
        return

    best_match = initial_result['metadatas'][0][0]
    # print("metadatas:", best_match)
    best_title = best_match["title"]
    print(f"Using semantically closest drama: {best_title}")

    base_embedding = initial_result['embeddings'][0][0] 

    # We look for similar dramas FIX TO TAKE MORE INTO ACCOUNT GENRES, COUNTRY, RATING
    similar_results = collection.query(
        query_embeddings=[base_embedding],
        n_results=100,  # on élargit pour filtrer ensuite
        include=["metadatas", "distances"]
    )

    all_matches = list(zip(similar_results["metadatas"][0], similar_results["distances"][0]))

    filtered = [
        (doc, dist)
        for doc, dist in all_matches
        if doc["title"].lower() != best_title.lower()
        and doc.get("is_popular", False)
        and doc.get("rating", 0) >= min_rating
        and "romance" in doc.get("genres", "").lower()
    ]

    filtered = sorted(filtered, key=lambda x: x[1])[:top_k]

    results = []
    for doc, dist in filtered:
        title = doc.get("title", "Unknown Title")
        country = doc.get("country", "Unknown Country")
        rating = doc.get("rating", "N/A")
        url = doc.get("url", f"https://mydramalist.com/{doc.get('id', '')}")
        # genres = ", ".join(ast.literal_eval(doc.get("genres", "[]"))) if isinstance(doc.get("genres"), str) else ""

        raw_genres = doc.get("genres", "[]")

        try:
            # Vérifie que c'est une chaîne qui ressemble à une liste avant d'utiliser literal_eval
            if isinstance(raw_genres, str) and raw_genres.strip().startswith("["):
                genres_list = ast.literal_eval(raw_genres)
                genres = ", ".join(genres_list)
            else:
                genres = raw_genres if isinstance(raw_genres, str) else ""
        except (ValueError, SyntaxError):
            genres = ""
        tags = ", ".join(doc.get("tags", [])) if isinstance(doc.get("tags"), list) else ""

        results.append({
            "title": title,
            "country": country,
            "rating": rating,
            "distance": dist,
            "url": url,
            "genres": genres,
            "tags": tags
        })

        if not return_streamlit:
            print(f"🎬 {title} ({country}) — ⭐ {rating} (distance: {dist:.4f})")
            if genres:
                print(f"Genres: {genres}")
            if tags:
                print(f"Tags: {tags}")
            print(f"   ➤ {url}\n")

    if return_streamlit:
        return results
        
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python similarity_case.py prompt \"your prompt here\"")
        print("  python similarity_case.py similar \"Drama Title\"")
        sys.exit(1)

    mode = sys.argv[1]
    input_text = " ".join(sys.argv[2:])

    if mode == "prompt":
        recommend_from_prompt(input_text)
    elif mode == "similar":
        recommend_similar_drama(input_text)
    else:
        print("Unknown mode. Use 'prompt' or 'similar'.")