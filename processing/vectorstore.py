from langchain_community.vectorstores import FAISS
from config import VECTORSTORE_DIR
import os

def create_vectorstore(docs, embeddings):
    vectorstore = FAISS.from_documents(docs, embeddings)
    vectorstore.save_local(VECTORSTORE_DIR)
    return vectorstore

def load_vectorstore(embeddings):
    if os.path.exists(VECTORSTORE_DIR):
        return FAISS.load_local(VECTORSTORE_DIR, embeddings, allow_dangerous_deserialization=True)
    return None