from rag.retriever import retrieve_docs
from langchain_community.llms import Ollama
from database import save_interaction, get_recent_interactions
from tools.patent_search import get_patent_results, format_patent_context
from utils import delete_uploaded_data
# -----------------------------
# Decide if Patent Search Needed
# -----------------------------
def needs_patent_search(query):

    q = query.lower()

    keywords = [
        "patent",
        "invention",
        "novel",
        "prior art",
        "similar patent",
        "existing patent",
        "google patent",
        "search patent",
        "is there existing patent",
        "is there any patent",
        "can this patent be acceptable",
    ]

    return any(word in q for word in keywords)


# -----------------------------
# Question Classifier
# -----------------------------
def classify_question(query):

    q = query.lower()

    if q.startswith("what is") or q.startswith("define"):
        return "definition"
    elif q.startswith("how"):
        return "procedural"
    elif "vs" in q or "difference" in q:
        return "comparative"
    elif q.startswith("when"):
        return "historical"
    else:
        return "general"


# -----------------------------
# Initialize LLM
# -----------------------------
llm = Ollama(
    model="mistral",
    temperature=0.0,
    num_predict=4096  # Increased to prevent abrupt cutoffs
)


# -----------------------------
# Main QA Function
# -----------------------------
def generate_answer(vectorstore, query):

    q_type = classify_question(query)

    # Use the LLM to classify the intent automatically
    intent_prompt = f"""Analyze this question: '{query}'
Classify it into exactly ONE of these five words:
WEB - if the user is explicitly asking to search the internet/web for existing patents.
DOCUMENT - if the user is asking about "this document", "the uploaded pdf", or referencing specific text from the provided file.
DELETE - if the user is asking to delete, remove, or clear the uploaded document, pdf, or database.
GENERAL - if the user is asking a general knowledge question about intellectual property, laws, or definitions not tied to a specific document.
OFF_TOPIC - if the question is completely unrelated to Intellectual Property, patents, legal matters, or the uploaded document (e.g., math, programming, cooking, random chat).

Reply ONLY with the single word."""

    intent = llm.invoke(intent_prompt).strip().upper()
    print("LLM Intent Classification:", intent)

    if "OFF_TOPIC" in intent:
        answer = "Hey! Nice try, but I am strictly a specialized AI for Intellectual Property Rights (IPR) and Law. I cannot answer random questions! Please ask me something related to patents, copyrights, or your uploaded document. 👨‍🏫"
        save_interaction(question=query, question_type="off_topic", context="", answer=answer)
        return answer

    # =====================================
    # CASE 1: PATENT SEARCH QUERY
    # =====================================
    if "WEB" in intent:

        patent_results = get_patent_results(query)

        print("Patent results:", patent_results)

        patent_context = format_patent_context(patent_results)

        prompt = f"""
You are a Patent Research Assistant.

Answer the user's question using ONLY the patent search results.

Patent Search Results:
{patent_context}

Question:
{query}

Instructions:
- Identify relevant patents
- Mention title and link if useful
- If nothing relevant exists say:
  "No relevant patents found."

Answer:
"""

        response = llm.invoke(prompt)
        answer = response.strip()

        save_interaction(
            question=query,
            question_type="patent_search",
            context=patent_context,
            answer=answer
        )

        return answer


    # =====================================
    # CASE 2: DOCUMENT RAG QUERY
    # =====================================
    elif "DOCUMENT" in intent:
        docs = retrieve_docs(vectorstore, query, k=5)

        doc_context = "\n\n".join([doc.page_content for doc in docs])

        if not doc_context.strip():
            answer = "I couldn't find anything related to that in the uploaded document."
            save_interaction(question=query, question_type=q_type, context="", answer=answer)
            return answer

        if q_type == "definition":
            instruction = "Give a short 3-4 line definition."
        elif q_type == "procedural":
            instruction = "Explain clearly in bullet points."
        elif q_type == "comparative":
            instruction = "Compare clearly in table format."
        elif q_type == "historical":
            instruction = "Mention dates and legal context clearly."
        else:
            instruction = "Give a clear and concise answer."

        history_rows = get_recent_interactions(limit=3)
        memory_context = ""
        if history_rows:
            memory_context = "\n--- PAST CONVERSATION MEMORY ---\n"
            for row in reversed(history_rows):
                memory_context += f"Previous user question: {row[2]}\nYour previous answer: {row[5]}\n\n"
            memory_context += "--- END OF PAST MEMORY ---\n"
            memory_context += "INSTRUCTION: Look at how you framed your answers in the past examples above. Maintain this exact style, tone, and formatting in your new answer.\n"

        prompt = f"""
You are a fun and enthusiastic teacher specializing in Intellectual Property Law! 
Always start your response with something like "Hey! Here are the things..."

STRICT RULES:
- Answer ONLY using the provided context.
- Keep your tone cheerful, educational, and engaging like a fun teacher.
- ALWAYS end your response with an engaging follow-up: either a relevant "Did you know?" fun fact, OR a friendly question asking what they want to explore next about this topic to keep the conversation going!

{memory_context}

Context:
{doc_context}

Question:
{query}

Instruction:
{instruction}

Answer:
"""
        response = llm.invoke(prompt)
        answer = response.strip()

        save_interaction(question=query, question_type=q_type, context=doc_context, answer=answer)
        return answer

    # =====================================
    # CASE 3: DELETE INTENT 
    # =====================================
    elif "DELETE" in intent:
        delete_uploaded_data()
        answer = "I have successfully deleted the uploaded PDF, cleared my memory of the document, and reset our conversation history. You can upload a new document whenever you're ready!"
        save_interaction(question=query, question_type="delete", context="", answer=answer)
        return answer

    # =====================================
    # CASE 4: GENERAL KNOWLEDGE 
    # =====================================
    else:
        history_rows = get_recent_interactions(limit=3)
        memory_context = ""
        if history_rows:
            memory_context = "\n--- PAST CONVERSATION MEMORY ---\n"
            for row in reversed(history_rows):
                memory_context += f"Previous user question: {row[2]}\nYour previous answer: {row[5]}\n\n"
            memory_context += "--- END OF PAST MEMORY ---\n"
            memory_context += "INSTRUCTION: Look at how you framed your answers in the past examples above. Maintain this exact style, tone, and formatting in your new answer.\n"

        prompt = f"""
You are a fun and enthusiastic teacher specializing in Intellectual Property Law! 
Always start your response with something like "Hey! Here are the things..."

STRICT RULES:
- You are strictly an Intellectual Property Rights (IPR) AI model.
- If the user's question is somehow NOT about law, intellectual property, patents, or related fields, you MUST completely refuse to answer it. Politely state that you only answer IPR-related questions.
- Answer based on your general knowledge.
- Keep your tone cheerful, educational, and engaging like a fun teacher.
- ALWAYS end your response with an engaging follow-up: either a relevant "Did you know?" fun fact, OR a friendly question asking what they want to explore next about this topic to keep the conversation going!

{memory_context}

Question:
{query}

Answer:
"""
        response = llm.invoke(prompt)
        answer = response.strip()

        save_interaction(question=query, question_type=q_type, context="General Knowledge", answer=answer)
        return answer


# -----------------------------
# PDF Scanner Function
# -----------------------------
def scan_pdf(docs, summary_length="500 words"):
    doc_context = "\n\n".join([doc.page_content for doc in docs])
    
    prompt = f"""
You are a fun and energetic teacher! 
Please analyze and scan the following legal document (or patent) and explain it in a cheerful, educational way. 
You MUST begin your response with exactly: "Here is the summarised version of ur pdf..."

Crucial Instruction: Your summary MUST be approximately {summary_length} long! Do not ignore this length requirement.

Finally, at the very end of the summary, ALWAYS add an engaging follow-up question or a fun related fact to keep the user interested and encourage them to ask more questions!

Document Content:
{doc_context}

Provide a clear and well-structured summary, keeping that fun teacher vibe!
"""
    
    response = llm.invoke(prompt)
    answer = response.strip()
    
    return answer