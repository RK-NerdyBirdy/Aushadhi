import numpy as np

class EmbeddingStore:
    def __init__(self):
        self.vectors = []
        self.metadata = []

    def add(self, embedding, metadata):
        self.vectors.append(embedding)
        self.metadata.append(metadata)

    def as_numpy(self):
        return np.array(self.vectors)

    def get_metadata(self, index):
        return self.metadata[index]
