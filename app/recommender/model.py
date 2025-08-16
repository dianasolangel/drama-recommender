import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def build_profile(user_dramas):
    texts = [d["tags"] + " " + d["synopsis"] for d in user_dramas]
    return TfidfVectorizer().fit_transform(texts)

def recommend_for_user(user_dramas, candidate_dramas):
    vectorizer = TfidfVectorizer()
    user_texts = [d["tags"] + " " + d["synopsis"] for d in user_dramas]
    candidate_texts = [d["tags"] + " " + d["synopsis"] for d in candidate_dramas]

    tfidf_matrix = vectorizer.fit_transform(user_texts + candidate_texts)
    similarity = cosine_similarity(tfidf_matrix[:len(user_dramas)], tfidf_matrix[len(user_dramas):])

    avg_scores = similarity.mean(axis=0)
    sorted_indices = avg_scores.argsort()[::-1]

    recommendations = [candidate_dramas[i] for i in sorted_indices[:10]]
    return recommendations
