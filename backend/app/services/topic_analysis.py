"""Run BERTopic on documents to discover topics from scratch."""

import numpy as np
from bertopic import BERTopic
from hdbscan import HDBSCAN
from sentence_transformers import SentenceTransformer
from umap import UMAP
from sklearn.feature_extraction.text import CountVectorizer
from bertopic.representation import KeyBERTInspired, MaximalMarginalRelevance


def analyze_topics(
    embedding_model: SentenceTransformer, docs: list[str]
) -> dict:
    """Fit a fresh BERTopic model on docs and return structured results."""
    # Scale min_cluster_size to dataset: at least 3, at most 5% of docs
    min_cluster_size=max(3, min(10, len(docs) //20))
    umap_n_neighbors=15
    umap_n_components=5
    nr_topics=10  # Cap the number of topics to 8
    top_n_words=15  # More words for descriptive labels
    n_gram_range=(1, 4)
    umap_model = UMAP(
        n_neighbors=umap_n_neighbors,
        n_components=umap_n_components,
        min_dist=0.0,
        metric='cosine',        
    )
    
    hdbscan_model = HDBSCAN(
        min_cluster_size=min_cluster_size,
        metric='euclidean',
        cluster_selection_method='eom',
        prediction_data=True
    )
    
    vectorizer_model = CountVectorizer(
        stop_words="english",
        ngram_range=n_gram_range,
        min_df=2
    )
        
    keybert_model = KeyBERTInspired()
    mmr_model = MaximalMarginalRelevance(diversity=0.3)
    
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
        nr_topics=nr_topics,
        top_n_words=top_n_words
    )
    topics, probs = topic_model.fit_transform(docs)

    # Build per-topic info
    topic_ids = sorted(set(topics))
    topic_results = []
    for tid in topic_ids:
        indices = [i for i, t in enumerate(topics) if t == tid]
        count = len(indices)
        topic_words = topic_model.get_topic(tid) if tid != -1 else None
        keywords = [w for w, _ in (topic_words or [])[:10]]
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
