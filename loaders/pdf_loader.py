from langchain_community.document_loaders import PyPDFLoader

def load_pdf(filepath):
    loader = PyPDFLoader(filepath)
    docs = loader.load()
    return docs