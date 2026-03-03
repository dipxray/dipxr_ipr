from flask import Blueprint, request, render_template
from processing.embeddings import get_embeddings
from processing.vectorstore import load_vectorstore
from rag.qa_chain import generate_answer

query_bp = Blueprint("query", __name__)

@query_bp.route("/query", methods=["POST"])
def query():
    question = request.form["question"]

    embeddings = get_embeddings()
    vectorstore = load_vectorstore(embeddings)

    # Let QA chain handle retrieval + augmentation
    answer = generate_answer(vectorstore, question)

    return render_template("index.html", answer=answer)