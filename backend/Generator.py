# LAST MODIFIED BY: Michael Tolentino
# LAST MODIFIED DATE: SEPT 3, 2025

from transformers import AutoModelForCausalLM, AutoTokenizer

class Generator:
    """
    A class to generate responses using a language model based on user queries and provided contexts.

    Attributes:
        model_name (str): The name of the pre-trained model to use.
    Methods:
        generate(query, contexts, section_numbers): Generates a response based on the query and contexts.
    """
    
    def __init__(self, model_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name).to("cuda")

    def generate(self, query, contexts, section_numbers):
        """
        Generates a response based on the query and contexts.
        
        Parameters:
            - query (str): The user's query.
            - contexts (list of str): The contexts from the manual to base the response on.
            - section_numbers (list of int): The page numbers of the context in the manual corresponding to the contexts.

        Returns:
            - str: The generated response.
        """
        context_str = "\n".join(
            [f"[{i+1}] content: {txt} page: {pg}" for i, (txt, pg) in enumerate(zip(contexts, section_numbers))]
        )

        messages = [
            {"role": "system", "content": "You are a helpful assistant specialized in Engineering Manuals. Answer ONLY using the given manual context. If you cannot find the answer in the context, respond with 'I don't know.'"},
            {"role": "user", "content": f"""Context:\n{context_str}\n\nQuestion: {query}\n\nAnswer concisely and provide references in the form (Answer: actual_answer, Section Title: section_title, Page: page_start)."""}
        ]

        # Use HuggingFace chat template
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(prompt, return_tensors="pt").to("cuda")

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=256,
            eos_token_id=self.tokenizer.eos_token_id,
        )

        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
