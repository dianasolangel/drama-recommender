import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from chromadb import PersistentClient
from tqdm import tqdm


# We load the dataset
df = pd.read_csv("../data/processed/dramas_with_popularity_flag.csv")

# We clean and prepare the data
df['popularity'] = pd.to_numeric(df['popularity'], errors='coerce')
df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
df = df.dropna(subset=['synopsis'])

# We build the text field for embeddings
def build_text(row):
    tags = row.get("tags", "")
    if isinstance(tags, list):
        tags = " ".join(tags)
    return f"{tags} {row['synopsis']}"

df['text'] = df.apply(build_text, axis=1)
df = df[df['text'].notnull() & (df['text'].str.strip() != "")]

# We generate embeddings
model = SentenceTransformer("all-MiniLM-L6-v2")
texts = df['text'].tolist()
embeddings = model.encode(
    texts,
    show_progress_bar=True,
    batch_size=32,
    convert_to_numpy=True 
)

chroma_client = PersistentClient(path="chroma_db") 
collection = chroma_client.get_or_create_collection(name="dramas")

# Saving data to chroma DB

docs = df['text'].tolist()
meta = df[['title', 'id', 'country', 'rating', 'genres', 'is_popular', 'synopsis']].to_dict(orient="records")
ids = [f"drama-{i}" for i in df['id']]

batch_size = 1000

for i in tqdm(range(0, len(docs), batch_size), desc="Inserting into Chroma"):
    collection.add(
        documents=docs[i:i+batch_size],
        embeddings=embeddings[i:i+batch_size],
        metadatas=meta[i:i+batch_size],
        ids=ids[i:i+batch_size]
    )
    
print("ChromaDB built and saved.")
print("Total docs saved:", collection.count())