import numpy as np

class Retriever:
    def __init__(self, embedding_store):
        self.store = embedding_store

    def retrieve(self, query_embedding, top_k=5):
        vectors = self.store.as_numpy()

        if len(vectors) == 0:
            return []

        similarities = np.dot(vectors, query_embedding) / (
            np.linalg.norm(vectors, axis=1) * np.linalg.norm(query_embedding)
        )

        top_indices = similarities.argsort()[-top_k:][::-1]

        return [
            self.store.get_metadata(i)
            for i in top_indices
        ]
