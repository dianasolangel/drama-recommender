import requests
import pandas as pd
import time
from src.utils import load_params
from tqdm import tqdm

def fetch_watchlist(params):
    username = params["fetch"]["username"]
    url = f"https://kuryana.tbdh.app/dramalist/{username}"

    res = requests.get(url)
    res.raise_for_status()
    data = res.json()["data"]["list"]

    all_dramas = []
    for status, content in data.items():
        for item in content["items"]:
            all_dramas.append({
                "name": item["name"],
                "id": item["id"].split("-")[0],
                "score": float(item["score"]),
                "episode_seen": int(item["episode_seen"]),
                "episode_total": int(item["episode_total"]),
                "status": status
            })

    df = pd.DataFrame(all_dramas)
    df.to_csv(params["data"]["raw_watchlist"], index=False)
    print("✅ Watchlist saved.")

def fetch_all_dramas(params):
    BASE_URL = "https://kuryana.tbdh.app"
    YEARS = range(2015, 2026)
    QUARTERS = [1, 2, 3, 4]
    TARGET_COUNTRIES = params["fetch"]["countries"]
    MIN_RATING = params["fetch"]["min_rating"]

    all_dramas = []
    for year in YEARS:
        for q in QUARTERS:
            url = f"{BASE_URL}/seasonal/{year}/{q}"
            print(f"Fetching: {url}")
            try:
                res = requests.get(url)
                res.raise_for_status()
                dramas = res.json()
            except Exception as e:
                print(f"Erreur sur {year} Q{q} : {e}")
                continue
            
            for drama in tqdm(dramas, desc=f"  Enriching {year} Q{q}"):
                try:
                    if (
                        drama.get("country") in TARGET_COUNTRIES and
                        (drama.get("rating") or 0) >= MIN_RATING and
                        drama.get("type") == "Drama" and
                        drama.get("content_type") in ["Korean Drama", "Japanese Drama", "Chinese Drama"]
                    ):
                        # Fallback synopsis (if detailed fails)
                        fallback_synopsis = drama.get("synopsis")
                        drama_id = drama.get("id")

                        # Fetch full details
                        try:
                            detail_url = f"{BASE_URL}/id/{drama_id}"
                            detail_res = requests.get(detail_url)
                            detail_res.raise_for_status()
                            full_data = detail_res.json()
                            full_synopsis = full_data["data"].get("synopsis", fallback_synopsis)
                            time.sleep(0.2)  # polite delay
                        except:
                            full_synopsis = fallback_synopsis

                        all_dramas.append({
                            "id": drama_id,
                            "title": drama.get("title"),
                            "year": year,
                            "quarter": q,
                            "country": drama.get("country"),
                            "type": drama.get("type"),
                            "content_type": drama.get("content_type"),
                            "rating": drama.get("rating"),
                            "ranking": drama.get("ranking"),
                            "popularity": drama.get("popularity"),
                            "genres": drama.get("genres"),
                            "synopsis": full_synopsis,
                            "url": f"https://mydramalist.com{drama.get('url')}"
                        })
                except Exception as e:
                    print(f"  ⚠️ Skipped a drama due to error: {e}")

            time.sleep(0.5)

    df = pd.DataFrame(all_dramas)
    df.to_csv(params["data"]["raw_all_dramas"], index=False)
    print(f"\n✅ All dramas enriched and saved to {params['data']['raw_all_dramas']}")

if __name__ == "__main__":
    params = load_params()
    fetch_watchlist(params)
    fetch_all_dramas(params)