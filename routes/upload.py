import os
from flask import Blueprint, request, redirect, render_template
from loaders.pdf_loader import load_pdf
from processing.splitter import split_docs
from processing.embeddings import get_embeddings
from processing.vectorstore import create_vectorstore
from config import RAW_DIR
from rag.qa_chain import scan_pdf

upload_bp = Blueprint("upload", __name__)

@upload_bp.route("/upload", methods=["POST"])
def upload_file():
    file = request.files["file"]
    filepath = os.path.join(RAW_DIR, file.filename)
    file.save(filepath)

    docs = load_pdf(filepath)
    split_documents = split_docs(docs)
    embeddings = get_embeddings()
    create_vectorstore(split_documents, embeddings)

    wants_summary = request.form.get("wants_summary")
    summary_length = request.form.get("summary_length", "500 words")

    if wants_summary == "yes":
        scan_result = scan_pdf(docs, summary_length)
    else:
        scan_result = "PDF successfully loaded into memory! I've read all the pages and am ready for your questions."

    return render_template("index.html", answer=scan_result)