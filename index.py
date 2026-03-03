from loaders.pdf_loader import load_pdf
from processing.splitter import split_docs
from processing.embeddings import get_embeddings
from processing.vectorstore import create_vectorstore

# ------------------------
# STEP 1: Load PDF
# ------------------------
documents = load_pdf("data/ipr.pdf")
print("📄 Documents loaded:", len(documents))

if len(documents) == 0:
    print("❌ No documents loaded. Check your PDF path or file.")
    exit()

# ------------------------
# STEP 2: Split Documents
# ------------------------
chunks = split_docs(documents)
print("✂️ Chunks created:", len(chunks))

if len(chunks) == 0:
    print("❌ No chunks created. PDF may not contain extractable text.")
    exit()

# ------------------------
# STEP 3: Load Embeddings
# ------------------------
embeddings = get_embeddings()
print("🧠 Embeddings model loaded")

# ------------------------
# STEP 4: Create Vectorstore
# ------------------------
vectorstore = create_vectorstore(chunks, embeddings)
print("📦 Vectorstore created")

# ------------------------
# STEP 5: Save
# ------------------------
vectorstore.save_local("data/vectorstore")
print("✅ Index created successfully!")