from rag.prompts import LEGAL_PROMPT
from transformers import pipeline
import torch

# Load LLM once (global)
generator = pipeline(
    "text-generation",
    model="google/flan-t5-base",
    torch_dtype=torch.float16,
    device_map="auto",
    dtype=torch.float16
)

def generate_answer(docs, question):
    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = LEGAL_PROMPT.format(
        context=context,
        question=question
    )

    response = generator(
        prompt,
        max_new_tokens=512,
        temperature=0.2,
        do_sample=False
    )

    return response[0]["generated_text"]