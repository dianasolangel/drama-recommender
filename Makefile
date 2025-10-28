SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c

# ====== PATHS FROM params.yaml ======
WATCHLIST = data/raw/watchlist.csv
ALL_DRAMAS = data/raw/all_dramas.csv
MERGED = data/interim/merged_watchlist.csv
PROCESSED = data/processed/dramas_with_popularity_flag.csv
CHROMA = src/chroma_db

# ====== Fetching Raw Data ======

$(WATCHLIST):
	poetry run python -m src.scraper.fetch_data --watchlist-only

$(ALL_DRAMAS):
	poetry run python -m src.scraper.fetch_data --dramas-only

# ====== Preprocessing / Merging ======

$(PROCESSED): $(WATCHLIST) $(ALL_DRAMAS)
	poetry run python -m src.preprocessing.merge_and_flag

# ====== Embedding to Chroma ======

$(CHROMA)/chroma.sqlite3: $(PROCESSED)
	poetry run python -m src.embedding.embed_to_chroma

# # ====== Upload to Hugging Face Datasets LATER ======

# upload-dataset: $(PROCESSED)
# 	poetry run python -m src.upload.save_dataset_to_hf

# upload-model:
# 	poetry run python -m src.upload.save_model_to_hf

# ====== Manual Convenience Targets ======

fetch:
	poetry run python -m src.scraper.fetch_data

prepare_dirs:
	mkdir -p data/interim

merge: prepare_dirs
	poetry run python -m src.preprocessing.merge_and_flag
	
embed:
	poetry run python -m src.embeddings.generate_embeddings

# ====== Full Pipeline ======

all: $(CHROMA)/chroma.sqlite3

# ====== Cleaning ======
clean:
	rm -rf data/interim/*
	rm -rf src/chroma_db/*
	rm -f $(WATCHLIST) $(ALL_DRAMAS) $(PROCESSED)
