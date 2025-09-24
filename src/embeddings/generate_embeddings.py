import pandas as pd
from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient
from src.utils import load_params
from tqdm import tqdm

def generate_embeddings(params):
    df = pd.read_csv(params["data"]["processed_dataset"])
    model = SentenceTransformer(params["embedding"]["model_name"])
    texts = df["text"].tolist()
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)

    ids = [f"drama-{i}" for i in df["id"]]
    metadatas = df[["title", "country", "rating", "is_popular"]].to_dict(orient="records")

    chroma_client = PersistentClient(path=params["embedding"]["chroma_path"])
    collection = chroma_client.get_or_create_collection(name=params["embedding"]["collection_name"])

    # On nettoie la collection avant d'ajouter de nouveaux embeddings
    collection.delete(ids=ids)
    batch_size = 1000
    for i in tqdm(range(0, len(texts), batch_size)):
        collection.add(
            ids=ids[i:i+batch_size],
            documents=texts[i:i+batch_size],
            embeddings=embeddings[i:i+batch_size],
            metadatas=metadatas[i:i+batch_size]
        )
    print("✅ Embeddings stored in ChromaDB.")

if __name__ == "__main__":
    params = load_params()
    generate_embeddings(params)