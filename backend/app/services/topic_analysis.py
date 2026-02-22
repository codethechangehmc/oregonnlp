"""Run BERTopic on documents to discover topics from scratch."""

import numpy as np
from bertopic import BERTopic
from hdbscan import HDBSCAN
from sentence_transformers import SentenceTransformer
from umap import UMAP
from sklearn.feature_extraction.text import CountVectorizer
from bertopic.representation import KeyBERTInspired, MaximalMarginalRelevance


def _stem_key(s: str) -> str:
    """Crude stem for dedupe: same root (e.g. hatchery/hatcheries, fish/fishing) maps to same key."""
    s = s.lower().strip()
    if len(s) <= 4:
        return s
    # Use first 4 chars so "fishing"->"fish", "fish"->"fish"; "hatchery"/"hatcheries"->"hatc"
    return s[:4]


def _dedupe_keywords(topic_words: list[tuple[str, float]] | None, max_words: int = 10) -> list[str]:
    """Keep diverse keywords: drop case duplicates, substring overlaps, and same-stem words (Fish/Fishing, Hatchery/Hatcheries)."""
    if not topic_words:
        return []
    seen_lower: set[str] = set()
    seen_stems: set[str] = set()
    result: list[str] = []
    for w, _ in topic_words:
        if len(result) >= max_words:
            break
        w_low = w.lower()
        if w_low in seen_lower:
            continue
        stem = _stem_key(w_low)
        if stem in seen_stems:
            continue
        if any(w_low in s or s in w_low for s in seen_lower):
            continue
        result.append(w)
        seen_lower.add(w_low)
        seen_stems.add(stem)
    return result


def analyze_topics(
    embedding_model: SentenceTransformer, docs: list[str]
) -> dict:
    """Fit a fresh BERTopic model on docs and return structured results."""
    # Scale min_cluster_size to dataset: at least 5, cap at ~7% of docs (fewer, larger clusters)
    min_cluster_size = max(5, min(15, len(docs) // 15))
    umap_n_neighbors = 15
    umap_n_components = 5
    nr_topics_max = 8  # Fewer, broader topics (merge overlapping fish/hatchery/salmon themes)
    top_n_words = 15  # More words for descriptive labels
    n_gram_range=(1, 4)
    umap_model = UMAP(
        n_neighbors=umap_n_neighbors,
        n_components=umap_n_components,
        min_dist=0.0,
        metric='cosine',
        random_state=42,
    )

    hdbscan_model = HDBSCAN(
        min_cluster_size=min_cluster_size,
        metric='euclidean',
        cluster_selection_method='eom',
        prediction_data=True,
    )
    
    vectorizer_model = CountVectorizer(
        stop_words="english",
        ngram_range=n_gram_range,
        min_df=2
    )
        
    keybert_model = KeyBERTInspired()
    mmr_model = MaximalMarginalRelevance(diversity=0.6)  # Prefer diverse keywords (avoid fish/fishing, hatchery/hatcheries)
    
    representation_model = {
        "KeyBERT": keybert_model,
        "MMR": mmr_model,
    }

    topic_model = BERTopic(
        language="english",
        calculate_probabilities=True,
        verbose=True,
        embedding_model=embedding_model,
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
        vectorizer_model=vectorizer_model,
        representation_model=representation_model,
        nr_topics="auto",  # Merge only similar topics (no forced merge of dissimilar ones)
        top_n_words=top_n_words,
    )
    topics, probs = topic_model.fit_transform(docs)

    # Merge similar topics and cap total to reduce duplicates
    num_before = len(set(t for t in topics if t != -1))
    if num_before > nr_topics_max:
        topic_model.reduce_topics(docs, nr_topics=nr_topics_max)
        topics = topic_model.topics_
        probs = topic_model.probabilities_ if topic_model.probabilities_ is not None else probs

    # Build per-topic info
    topic_ids = sorted(set(topics))
    topic_results = []
    for tid in topic_ids:
        indices = [i for i, t in enumerate(topics) if t == tid]
        count = len(indices)
        topic_words = topic_model.get_topic(tid) if tid != -1 else None
        keywords = _dedupe_keywords(topic_words, max_words=10)
        samples = [docs[i] for i in indices[:5]]

        topic_results.append({
            "topic_id": int(tid),
            "label": "",  # filled by LLM labeling
            "description": "",
            "category": "",
            "count": int(count),
            "percentage": round(count / len(docs) * 100, 1),
            "keywords": keywords,
            "sample_responses": samples,
        })

    # Per-document assignments
    assignments = []
    probs_array = np.array(probs) if probs is not None else None
    for i, (doc, tid) in enumerate(zip(docs, topics)):
        prob = 0.0
        if probs_array is not None:
            p = probs_array[i]
            if np.ndim(p) == 0:
                prob = float(p)
            elif len(p) > 0:
                prob = float(np.max(p))
        assignments.append({
            "id": i,
            "text": doc,
            "topic_id": int(tid),
            "topic_label": "",
            "probability": round(prob, 3),
        })

    return {
        "topics": topic_results,
        "assignments": assignments,
        "num_topics": len([t for t in topic_ids if t != -1]),
    }
