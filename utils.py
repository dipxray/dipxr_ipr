import os
import shutil
from config import RAW_DIR, VECTORSTORE_DIR
from database import clear_all_interactions

def delete_uploaded_data():
    """
    Clears the raw uploaded documents, the vectorstore database,
    and all past chat interactions from the history.
    """
    # 1. Empty the RAW_DIR
    if os.path.exists(RAW_DIR):
        for filename in os.listdir(RAW_DIR):
            file_path = os.path.join(RAW_DIR, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")

    # 2. Empty the VECTORSTORE_DIR
    if os.path.exists(VECTORSTORE_DIR):
        for filename in os.listdir(VECTORSTORE_DIR):
            file_path = os.path.join(VECTORSTORE_DIR, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")

    # 3. Clear database interactions
    clear_all_interactions()
