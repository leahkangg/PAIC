from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import pdfplumber
import os

# test message 

# -------------------------
# Flask setup
# -------------------------
app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------------------------
# OpenAI client
# -------------------------
client = OpenAI(api_key="YOURAPIKEY")

# -------------------------
# AI System Prompt
# -------------------------
SYSTEM_PROMPT = """
You are a friendly and knowledgeable financial assistant.
You help users with budgeting, saving, debt, credit score, and good financial habits.
Always respond clearly and practically.
"""

# -------------------------
# Global state (simple demo)
# -------------------------
chat_history = [{"role": "system", "content": SYSTEM_PROMPT}]
uploaded_pdf_text = None


# -------------------------
# PDF Text Extractor
# -------------------------
def extract_text(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


# -------------------------
# Routes
# -------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_pdf():
    global uploaded_pdf_text

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    uploaded_pdf_text = extract_text(path)

    return jsonify({"message": "PDF uploaded and processed successfully."})


@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "").strip()

    if not user_message:
        return jsonify({"response": "Please enter a message."})

    prompt = user_message

    # Attach PDF context if uploaded
    if uploaded_pdf_text:
        prompt += f"""

(Uploaded bank statement context:
{uploaded_pdf_text[:4000]}
)
"""

    chat_history.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=chat_history
    )

    assistant_reply = response.choices[0].message.content
    chat_history.append({"role": "assistant", "content": assistant_reply})

    return jsonify({"response": assistant_reply})


# -------------------------
# Run server
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)