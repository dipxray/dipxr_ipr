import os
from flask import Blueprint, request, redirect
from loaders.pdf_loader import load_pdf
from processing.splitter import split_docs
from processing.embeddings import get_embeddings
from processing.vectorstore import create_vectorstore
from config import RAW_DIR

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

    return redirect("/")