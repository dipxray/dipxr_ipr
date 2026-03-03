from transformers import pipeline
from langchain_huggingface import HuggingFacePipeline

# Create LLM once (outside function)
pipe=pipeline(
    "text-generation",
    model="google/flan-t5-small",
    max_new_tokens=64
)

llm = HuggingFacePipeline(pipeline=pipe)


def generate_queries(query):
    prompt = f"""Generate 3 different rephrasings of this query:
    {query}
    """

    response = llm.invoke(prompt)

    # Split into lines
    queries = response.split("\n")
    return [q.strip() for q in queries if q.strip()]


def retrieve_docs(vectorstore, query, k=5):

    base_retriever = vectorstore.as_retriever(search_kwargs={"k": k})

    queries = generate_queries(query)

    all_docs = []

    for q in queries:
        docs = base_retriever.invoke(q)
        all_docs.extend(docs)

    # Remove duplicates
    unique_docs = list({doc.page_content: doc for doc in all_docs}.values())

    return unique_docs