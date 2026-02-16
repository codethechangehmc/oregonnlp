"""Train and save BERTopic model from test_survey.csv."""

import os
import re
import sys
import random
from pathlib import Path

SEED = 42
random.seed(SEED)
os.environ["PYTHONHASHSEED"] = str(SEED)


import numpy as np
import pandas as pd


def clean_text(text: str) -> str:
    text = str(text).strip()
    text = re.sub(r"\s+", " ", text)
    return text


def preprocess_responses(responses: list[str], min_length: int = 2) -> list[str]:
    cleaned = [clean_text(r) for r in responses]
    cleaned = [r for r in cleaned if r and r.lower() not in ("", "nan", "none", "n/a")]
    return [r for r in cleaned if len(r.split()) >= min_length]


def main():
    project_root = Path(__file__).resolve().parent.parent
    csv_path = project_root / "notebooks" / "test_survey.csv"
    model_dir = project_root / "models" / "fishing_survey_bertopic"

    # Load data
    df = pd.read_csv(csv_path)
    raw = df.iloc[:, 0].dropna().astype(str).tolist()[1:]  # skip header row
    responses = preprocess_responses(raw)
    print(f"Preprocessed {len(raw)} -> {len(responses)} responses")

    # Seed numpy/torch after imports are available
    np.random.seed(SEED)
    import torch
    torch.manual_seed(SEED)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(SEED)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

    # Build model (same params as notebook cell 10)
    from bertopic import BERTopic
    from bertopic.representation import KeyBERTInspired, MaximalMarginalRelevance
    from hdbscan import HDBSCAN
    from sentence_transformers import SentenceTransformer
    from sklearn.feature_extraction.text import CountVectorizer
    from umap import UMAP

    topic_model = BERTopic(
        language="english",
        calculate_probabilities=True,
        verbose=True,
        embedding_model=SentenceTransformer("all-MiniLM-L6-v2"),
        umap_model=UMAP(
            n_neighbors=15,
            n_components=5,
            min_dist=0.0,
            metric="cosine",
            random_state=SEED,
        ),
        hdbscan_model=HDBSCAN(
            min_cluster_size=3,
            metric="euclidean",
            cluster_selection_method="eom",
            prediction_data=True,
        ),
        vectorizer_model=CountVectorizer(
            stop_words="english", ngram_range=(1, 4), min_df=2
        ),
        representation_model={
            "KeyBERT": KeyBERTInspired(),
            "MMR": MaximalMarginalRelevance(diversity=0.3),
        },
        nr_topics=8,
        top_n_words=15,
    )

    print("Training BERTopic model...")
    topic_model.fit_transform(responses)

    model_dir.mkdir(parents=True, exist_ok=True)
    topic_model.save(
        str(model_dir), serialization="safetensors", save_ctfidf=True
    )
    print(f"Model saved to {model_dir}")


if __name__ == "__main__":
    main()
