from langchain_community.llms import Ollama

# -----------------------------
# Initialize LLM for Router
# -----------------------------
llm = Ollama(
    model="mistral",
    temperature=0.0
)

# -----------------------------
# Intent Router Logic
# -----------------------------
def classify_intent(query):
    """
    Classifies the user's intent into one of five categories:
    - WEB: External patent/web search
    - DOCUMENT: Query related to the uploaded file
    - DELETE: Request to clear data/history
    - GENERAL: General IPR knowledge query
    - OFF_TOPIC: Unrelated content
    """
    intent_prompt = f"""Analyze this question: '{query}'
Classify it into exactly ONE of these five words:
WEB - if the user is explicitly asking to search the internet/web for patents, inventions, or the latest legal filings.
DOCUMENT - if the user is asking about "this document", "the uploaded pdf", or referencing specific text from the provided file.
DELETE - if the user is asking to delete, remove, or clear the uploaded document, pdf, or database.
GENERAL - if the user is asking a general knowledge question about intellectual property, laws, or definitions not tied to a specific document.
OFF_TOPIC - if the question is completely unrelated to Intellectual Property, patents, legal matters, or the uploaded document (e.g., math, programming, cooking, random chat).

Reply ONLY with the single word."""

    intent = llm.invoke(intent_prompt).strip().upper()
    print("ROUTER (YOU) Intent Classification:", intent)
    return intent
