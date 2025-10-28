import os
import pandas as pd
from src.utils import load_params
import re
import ast

def ensure_dir(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def merge_and_flag(params):
    """Merge the watchlist with the full drama dataset,
    add flags for popularity and watched status,
    and clean the dataset for embedding generation."""
    
    all_dramas = pd.read_csv(params["data"]["raw_all_dramas"])
    watchlist = pd.read_csv(params["data"]["raw_watchlist"])

    all_dramas["id"] = all_dramas["id"].astype(str)
    watchlist["id"] = watchlist["id"].astype(str)

    #Flags
    all_dramas["is_popular"] = all_dramas["popularity"] >= all_dramas["popularity"].quantile(0.85)
    all_dramas["watched"] = all_dramas["id"].isin(watchlist["id"])
    
    #The score I gave to the drama in the watchlist (NaN if not watched)
    watched_scores = watchlist[watchlist["status"] == "watched"].set_index("id")["score"]
    all_dramas["my_score"] = all_dramas["id"].map(watched_scores)

    ensure_dir(params["data"]["interim_merged"])
    all_dramas.to_csv(params["data"]["interim_merged"], index=False)

    #Cleaning for a better embedding
    cleaned = all_dramas.dropna(subset=["synopsis"]).copy()
    cleaned["synopsis"] = cleaned["synopsis"].str.replace(r"\(Source:.*?\)", "", regex=True).str.strip() # noise in the synopsis
    cleaned["text"] = cleaned["genres"].fillna('') + " " + cleaned["synopsis"] #Tags + Synopsis
    cleaned["text"] = cleaned["text"].str.strip()
    cleaned["alternative_titles"] = cleaned["alternative_titles"].apply(
    lambda x: ast.literal_eval(str(x).strip('"')) if pd.notnull(x) else [])
    cleaned["tags"] = cleaned["tags"].apply(
    lambda x: [
        t.replace(" (Vote tags)", "").strip()
        for t in ast.literal_eval(str(x).strip('"'))
    ] if isinstance(x, str) and str(x).strip().startswith("[") else [])
    cleaned = cleaned[cleaned["text"] != ""]
    
    ensure_dir(params["data"]["processed_dataset"])
    cleaned.to_csv(params["data"]["processed_dataset"], index=False)
    print("Merged and processed dataset saved.")

if __name__ == "__main__":
    params = load_params()
    merge_and_flag(params)