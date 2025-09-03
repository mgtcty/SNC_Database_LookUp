# LAST MODIFIED BY: Michael Tolentino
# LAST MODIFIED DATE: SEPT 3, 2025

from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class Retriever:
    """
    A class to handle the retrieval of relevant sections from the database (containing all the manual) based on user queries using vector embeddings.
    Attributes:
        embedding_model (str): The name of the pre-trained embedding model to use.
        embedding_dim (int): The dimension of the embeddings.

    Methods:
        add(contents, ids): Adds new sections to the vector index.
        search(query, top_k): Searches for the most relevant sections based on the query.
    """
    def __init__(self, embedding_model="all-MiniLM-L6-v2", embedding_dim=384):
        self.embedding_dim = embedding_dim
        self.embedding_model = SentenceTransformer(embedding_model)
        self.index = faiss.IndexFlatL2(embedding_dim)
        self.id_map = {}

    def add(self, contents, ids):
        """
        Adds new sections to the vector index.

        Parameters:
            - contents (list of str): The sections to be added to the index.
            - ids (list of int): The IDs corresponding to the sections.
        """
        embeddings = self.embedding_model.encode(contents, convert_to_numpy=True).astype("float32")
        self.index.add(embeddings)
        start = len(self.id_map)
        for i, section_id in enumerate(ids):
            self.id_map[start + i] = section_id

    def search(self, query, top_k=20):
        """
        Searches for the most relevant sections based on the query.
        Parameters:
            - query (str): The user's query.
            - top_k (int): The number of top relevant sections to retrieve.
        """
        query_vector = self.embedding_model.encode([query], convert_to_numpy=True).astype("float32")
        distances, indices = self.index.search(query_vector, top_k)
        return [self.id_map[idx] for idx in indices[0] if idx in self.id_map]