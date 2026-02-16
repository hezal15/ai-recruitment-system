from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Load SBERT model once
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text):
    return model.encode(text)

def compute_similarity(text1, text2):
    emb1 = get_embedding(text1)
    emb2 = get_embedding(text2)

    score = cosine_similarity(
        [emb1],
        [emb2]
    )[0][0]

    return round(score * 100, 2)
