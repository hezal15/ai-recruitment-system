from sentence_transformers import SentenceTransformer
import numpy as np

# Load MPNet model
model = SentenceTransformer('all-mpnet-base-v2')

def compute_similarity(text1, text2):
    """
    Compute cosine similarity between two texts using MPNet embeddings.
    """
    emb1 = model.encode(text1, convert_to_numpy=True)
    emb2 = model.encode(text2, convert_to_numpy=True)

    similarity = np.dot(emb1, emb2) / (
        np.linalg.norm(emb1) * np.linalg.norm(emb2)
    )

    return float(similarity)
