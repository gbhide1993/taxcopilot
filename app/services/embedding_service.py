from sentence_transformers import SentenceTransformer
import torch

print("Loading embedding model at startup...")

model = SentenceTransformer("BAAI/bge-small-en")


def generate_embedding(text: str):
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()
