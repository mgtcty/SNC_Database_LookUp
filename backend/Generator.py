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

    """
    models to consider:
    - TinyLlama/TinyLlama-1.1B-Chat-v1.0 (1.1B parameters: possible to use in production if DAPT and SFT are done)
    - microsoft/phi-2 (2.7B parameters) (not fit: ate a lot of memory, exceeded 16gb ram, not ideal for local deployment)
    - microsoft/Phi-3-mini-4k-instruct (3.82B parameters: probably worse than phi-2 since it uses higher vram)
    - unsloth/Qwen2.5-Coder-0.5B-Instruct (0.5B parameters: weak reasoning worse then tinyllama)
    - meta-llama/Llama-3.2-1B (currently using this one, 1.2B parameters: neutral reasoning, good english)
    """
    
    def __init__(self, model_name="meta-llama/Llama-3.2-1B-Instruct"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name).to("cuda")

    def cleanText(self, raw_response):
        """
        Extracts only the assistant's final response text from the raw LLaMA-style output.
        """
        # Find the last assistant header
        header_marker = "<|end_header_id|>"
        end_marker = "<|eot_id|>"

        # Locate the last occurrence of header_marker
        start_idx = raw_response.rfind(header_marker)
        if start_idx == -1:
            return raw_response.strip()  # fallback

        start_idx += len(header_marker)

        # Locate the first <|eot_id|> after that
        end_idx = raw_response.find(end_marker, start_idx)
        if end_idx == -1:
            return raw_response[start_idx:].strip()

        # Slice and clean
        return raw_response[start_idx:end_idx].strip()

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
            [f"[{i+1}] content: {contentText} page: {page}" for i, (contentText, page) in enumerate(zip(contexts, section_numbers))]
        )

        # for debugging purposes
        tokenized_contexts = self.tokenizer(context_str)
        print(context_str, "\n\n\n\n")
        print("the len of content tokens is: ",len(tokenized_contexts['input_ids']))

        messages = [
            {"role": "system", "content": "You are a helpful assistant specialized in Engineering Manuals and Engineering Principles. Answer ONLY using the given manual."},
            {"role": "user", "content": f"""Context:\n{context_str}\n\nQuestion: {query}\n\nAnswer concisely and accurately based on the above context."""}
        ]

        # Use HuggingFace chat template
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(prompt, return_tensors="pt").to("cuda")

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=256,
            eos_token_id=self.tokenizer.eos_token_id,
        )

        raw_response = self.tokenizer.decode(outputs[0], skip_special_tokens=False)
        clean_response = self.cleanText(raw_response)

        return clean_response
