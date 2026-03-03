import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
VECTORSTORE_DIR = os.path.join(DATA_DIR, "vectorstore")

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"