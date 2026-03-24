from flask import Flask, render_template
import os
from config import RAW_DIR, VECTORSTORE_DIR
from routes.upload import upload_bp
from routes.query import query_bp
from database import init_db


app = Flask(__name__)

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(VECTORSTORE_DIR, exist_ok=True)

app.register_blueprint(upload_bp)
app.register_blueprint(query_bp)


@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
    init_db()