from transformers import pipeline
from langchain_huggingface import HuggingFacePipeline

# -----------------------------
# Initialize LLM with randomness
# -----------------------------
pipe = pipeline(
    "text-generation",
    model="google/flan-t5-base",
    max_new_tokens=64,
    do_sample=True,       # Enable randomness
    temperature=0.7,      # Controls creativity
    top_k=50,             # Optional: sample from top-k tokens
)

llm = HuggingFacePipeline(pipeline=pipe)


# -----------------------------
# Generate multiple diverse rephrasings
# -----------------------------
def generate_queries(query, num_rephrasings=3):
    queries = []
    for _ in range(num_rephrasings):
        prompt = f"Rephrase this query in a different way:\n{query}"
        response = llm.invoke(prompt)
        queries.append(response.strip())
    # Remove exact duplicates if any
    unique_queries = list(dict.fromkeys(queries))
    return unique_queries


# -----------------------------
# Retrieve documents for multiple queries
# -----------------------------
def retrieve_docs(vectorstore, query, k=5):
    base_retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    
    # Generate diverse rephrasings
    queries = generate_queries(query, num_rephrasings=3)
    
    all_docs = []
    for q in queries:
        docs = base_retriever.invoke(q)
        all_docs.extend(docs)
    
    # Remove duplicates based on content
    unique_docs = list({doc.page_content: doc for doc in all_docs}.values())
    return unique_docs