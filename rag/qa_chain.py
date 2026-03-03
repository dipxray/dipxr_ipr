from rag.retriever import retrieve_docs
from langchain_community.llms import Ollama

# Initialize Mistral LLM once
llm = Ollama(
    model="mistral",
    temperature=0.0,
    num_predict=150 # deterministic for legal answers
)

def generate_answer(vectorstore, query):
    # Step 1: Retrieve documents
    docs = retrieve_docs(vectorstore, query, k=3)

    # Step 2: Merge context (limit size to avoid overload)
    context = "\n\n".join([doc.page_content[:400] for doc in docs])

    # Step 3: Optimized Augmented Prompt (shorter + stronger)
    prompt = f"""
You are a Legal AI Advisor specializing in Intellectual Property Law.

Answer ONLY using the provided context.
If the answer is not found, say:
"The answer is not available in the provided document."

Give a clear, structured, and concise response.

Context:
{context}

Question:
{query}

Answer in this format:
Short Answer:
"""

    # Step 4: Generate response
    response = llm.invoke(prompt)

    return response.strip()