from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient
from tqdm import tqdm
import pandas as pd
import ast

def generate_embeddings(params):
    df = pd.read_csv(params["data"]["processed_dataset"])

    # Handle alternative_titles if it's stored as stringified list
    if "alternative_titles" in df.columns:
        df["alternative_titles"] = df["alternative_titles"].apply(
            lambda x: ", ".join(ast.literal_eval(x)) if pd.notnull(x) else ""
        )
    else:
        df["alternative_titles"] = ""

    # Build enriched text field
    df["enriched_text"] = df.apply(
        lambda row: f"{row['title']} {row['alternative_titles']} {row['text']}",
        axis=1
    )

    model = SentenceTransformer(params["embedding"]["model_name"])
    texts = df["enriched_text"].tolist()
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)

    ids = [f"drama-{i}" for i in df["id"]]
    metadatas = df[["title", "country", "rating", "is_popular"]].to_dict(orient="records")

    chroma_client = PersistentClient(path=params["embedding"]["chroma_path"])
    collection = chroma_client.get_or_create_collection(name=params["embedding"]["collection_name"])

    # Clean collection before new insert
    collection.delete(ids=ids)

    batch_size = 1000
    for i in tqdm(range(0, len(texts), batch_size), desc="🔢 Inserting to Chroma"):
        collection.add(
            ids=ids[i:i+batch_size],
            documents=texts[i:i+batch_size],
            embeddings=embeddings[i:i+batch_size],
            metadatas=metadatas[i:i+batch_size]
        )
    print("✅ Embeddings with alternative names stored in ChromaDB.")