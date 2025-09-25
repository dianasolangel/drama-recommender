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


def get_all_drama_names(drama_id: int):
    url = f"https://kuryana.tbdh.app/id/{drama_id}"
    res = requests.get(url)

    if res.status_code == 200:
        data = res.json()["data"]
        main_title = data.get("title", "")
        native_titles = data.get("others", {}).get("native_title", [])
        also_known_as = data.get("others", {}).get("also_known_as", [])

        all_names = list({main_title, *native_titles, *also_known_as}) # unique names
        return all_names
    else:
        print(f"❌ Could not fetch titles for drama {drama_id} — Status: {res.status_code}")
        return []

def fetch_all_dramas(params):
    BASE_URL = "https://kuryana.tbdh.app"
    YEARS = range(2015, 2026)
    QUARTERS = [1, 2, 3, 4]
    TARGET_COUNTRIES = params["fetch"]["countries"]
    MIN_RATING = params["fetch"]["min_rating"]
    OUTPUT_PATH = params["data"]["raw_all_dramas"]

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
                print(f"Error on {year} Q{q}: {e}")
                continue

            for drama in tqdm(dramas, desc=f"  Enriching {year} Q{q}"):
                try:
                    if (
                        drama.get("country") in TARGET_COUNTRIES and
                        (drama.get("rating") or 0) >= MIN_RATING and
                        drama.get("type") == "Drama" and
                        drama.get("content_type") in ["Korean Drama", "Japanese Drama", "Chinese Drama"]
                    ):
                        fallback_synopsis = drama.get("synopsis")
                        drama_id = drama.get("id")
                        full_synopsis = fallback_synopsis
                        all_names = []

                        # Try to get full details
                        try:
                            detail_url = f"{BASE_URL}/id/{drama_id}"
                            detail_res = requests.get(detail_url)

                            if detail_res.status_code == 200:
                                full_data = detail_res.json()["data"]
                                full_synopsis = full_data.get("synopsis", fallback_synopsis)
                                all_names = get_all_drama_names(drama_id)
                            else:
                                print(f"Failed to fetch details for ID {drama_id}: {detail_res.status_code}")
                        except Exception as e:
                            print(f"Failed to fetch details for ID {drama_id}: {e}")

                        all_dramas.append({
                            "id": drama_id,
                            "title": drama.get("title"),
                            "alternative_titles": all_names,
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

                        time.sleep(0.2)  # polite delay
                except Exception as e:
                    print(f"Skipped a drama due to error: {e}")

            time.sleep(0.5)

    df = pd.DataFrame(all_dramas)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"\n✅ All dramas enriched and saved to {OUTPUT_PATH}")
if __name__ == "__main__":
    params = load_params()
    fetch_watchlist(params)
    fetch_all_dramas(params)