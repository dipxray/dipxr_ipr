from rag.retriever import retrieve_docs
from langchain_community.llms import Ollama
from database import save_interaction, get_recent_interactions
from tools.patent_search import get_patent_results, format_patent_context
from utils import delete_uploaded_data
from rag.router import classify_intent
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
    intent = classify_intent(query)

    if "OFF_TOPIC" in intent:
        answer = "Hey! Nice try, but I am strictly a specialized AI for Intellectual Property Rights (IPR) and Law. I cannot answer random questions! Please ask me something related to patents, copyrights, or your uploaded document. 👨‍🏫"
        save_interaction(question=query, question_type="off_topic", context="", answer=answer)
        return answer, "OFF_TOPIC"

    # =====================================
    # CASE 1: PATENT SEARCH QUERY
    # =====================================
    if "WEB" in intent:

        patent_results = get_patent_results(query)

        print("Patent results:", patent_results)

        patent_context = format_patent_context(patent_results)

        prompt = f"""
You are an expert Patent & IPR Research Assistant with deep browser access.

Answer the user's question by analyzing the provided web search and browser results. 
If the results contain deep context from a webpage, prioritize that information.

Web Search & Browser Results:
{patent_context}

Question:
{query}

Instructions:
- Provide a detailed analysis of relevant patents or filings found.
- Mention titles, patent numbers (if available), and source links.
- If the search results are insufficient to answer the question accurately, say so.
- Keep your tone professional and informative.

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

        return answer, "WEB"


    # =====================================
    # CASE 2: DOCUMENT RAG QUERY
    # =====================================
    elif "DOCUMENT" in intent:
        docs = retrieve_docs(vectorstore, query, k=5)

        doc_context = "\n\n".join([doc.page_content for doc in docs])

        if not doc_context.strip():
            answer = "I couldn't find anything related to that in the uploaded document."
            save_interaction(question=query, question_type=q_type, context="", answer=answer)
            return answer, "DOCUMENT"

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
You are a specialized Intellectual Property Law expert. 
Your goal is to provide highly accurate and professional answers based on the uploaded document.

STRICT RULES:
- Answer ONLY using the provided context from the document.
- If the answer is not in the document, explicitly state that.
- Keep your tone professional, yet direct and helpful.
- ALWAYS end your response with a professional follow-up question related to the document's content to assist the user further.

{memory_context}

Context from Uploaded Document:
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
        return answer, "DOCUMENT"

    # =====================================
    # CASE 3: DELETE INTENT 
    # =====================================
    elif "DELETE" in intent:
        delete_uploaded_data()
        answer = "I have successfully deleted the uploaded PDF, cleared my memory of the document, and reset our conversation history. You can upload a new document whenever you're ready!"
        save_interaction(question=query, question_type="delete", context="", answer=answer)
        return answer, "DELETE"

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
You are a highly knowledgeable Intellectual Property Law expert. 
Answer the user's general IPR-related question with precision and clarity.

STRICT RULES:
- You are strictly an Intellectual Property Rights (IPR) AI model.
- If the question is NOT related to law, intellectual property, patents, or related fields, politely refuse to answer.
- Keep your tone professional, informative, and direct.
- ALWAYS end your response with a professional follow-up question to keep the consultation going.

{memory_context}

Question:
{query}

Answer:
"""
        response = llm.invoke(prompt)
        answer = response.strip()

        save_interaction(question=query, question_type=q_type, context="General Knowledge", answer=answer)
        return answer, "GENERAL"


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