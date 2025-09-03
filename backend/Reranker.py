from sentence_transformers import CrossEncoder

class Reranker:
    """
    A class designed to increased accuracy of the overall rag model by reranking the top k sections retrieved from the database through cross-encoder.
    """
    def __init__(self, model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = CrossEncoder(model_name)

    def rerank(self, query, passages, top_k=5):
        """
        Reranks the given passages based on their relevance to the query.

        Parameters:
            - query (str): The user's query.
            - passages (list of str): The passages to be reranked.

        Returns:
            - list of tuples: Each tuple contains a passage and its corresponding score, sorted by score in descending order.
        """
        # Prepare the input for the cross-encoder
        inputs = [[query, passage] for passage in passages]
        
        # Get the relevance scores
        scores = self.model.predict(inputs)
        
        # Combine passages with their scores and sort them
        rankedPassage = sorted(zip(passages, scores), key=lambda x: x[1], reverse=True)
        
        return [p for p, _ in rankedPassage[:top_k]]