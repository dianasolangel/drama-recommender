from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient
from tqdm import tqdm
import pandas as pd
import ast
import yaml

def safe_list_to_str(x):
    try:
        if pd.isna(x):
            return ""
        parsed = ast.literal_eval(str(x).strip())
        if isinstance(parsed, list):
            return " ".join(str(i).strip() for i in parsed)
        return str(x)  # fallback
    except Exception:
        return str(x)
    
def generate_embeddings(params):
    "To generate and store embeddings in ChromaDB for semantic search and recommendations"

    df = pd.read_csv(params["data"]["processed_dataset"])
    
    df["alternative_titles"] = df["alternative_titles"].apply(safe_list_to_str)
    df["genres"] = df["genres"].apply(safe_list_to_str)
    df["tags"] = df["tags"].apply(safe_list_to_str)
    
    # df["alternative_titles"] = df["alternative_titles"].apply(
    #     lambda x: ", ".join(ast.literal_eval(x)) if pd.notnull(x) else ""
    # )
    # df["genres"] = df["genres"].apply(
    #     lambda x: " ".join(ast.literal_eval(x)) if pd.notnull(x) else ""
    # )
    # df["tags"] = df["tags"].apply(
    #     lambda x: " ".join(ast.literal_eval(x)) if pd.notnull(x) else ""
    # )

    #Enriched text column for semantic similarity
    df["enriched_text"] = (
        df["title"].fillna("") + " " +
        df["alternative_titles"] + " " +
        df["genres"] + " " +
        df["tags"] + " " +
        df["synopsis"].fillna("")
    )

    model = SentenceTransformer(params["embedding"]["model_name"])
    texts = df["enriched_text"].tolist()
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)

    ids = [f"drama-{i}" for i in df["id"]]
    metadatas = df[["id", "title", "country", "rating", "is_popular", "genres", "tags", "url"]].to_dict(orient="records")


    # Store in ChromaDB
    chroma_client = PersistentClient(path=params["embedding"]["chroma_path"])
    collection = chroma_client.get_or_create_collection(name=params["embedding"]["collection_name"])
    collection.delete(ids=ids) # we first delete to avoid duplicates and have a fresh start

    for i in tqdm(range(0, len(texts), 1000), desc="Inserting to Chroma"):
        collection.add(
            ids=ids[i:i+1000],
            documents=texts[i:i+1000],
            embeddings=embeddings[i:i+1000],
            metadatas=metadatas[i:i+1000]
        )

    print("Embeddings enriched with tags and alt titles stored in ChromaDB.")

if __name__ == "__main__":
    print("Starting embedding process...")
    with open("params.yaml", "r") as f:
        params = yaml.safe_load(f)
    generate_embeddings(params)