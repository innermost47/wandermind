from flask import (
    Flask,
    jsonify,
    request,
    Response,
    render_template,
    session,
    stream_with_context,
)
from services.wikipedia import get_wikipedia_data
from services.llm import query_llm
from services.whisper import transcribe_audio
import json
from dotenv import load_dotenv
import os
from urllib.parse import urlparse
import sys

load_dotenv()

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/wikipedia", methods=["POST"])
def wikipedia():
    data = request.json
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if not latitude or not longitude:
        return jsonify({"error": "Invalid location data"}), 400

    wikipedia_content = get_wikipedia_data(latitude, longitude)

    if not wikipedia_content:
        return (
            jsonify({"error": "No relevant information found for this location."}),
            404,
        )
    session["wikipedia_content"] = wikipedia_content

    def generate():
        for chunk in query_llm(
            "Présentez ce lieu comme un guide touristique.", wikipedia_content
        ):
            yield json.dumps(chunk).encode("utf-8")

    return Response(generate(), mimetype="text/event-stream")


def llm():
    data = request.json
    question = data.get("question")
    context = session.get("wikipedia_content")
    if not context:
        return (
            jsonify(
                {
                    "error": "No location context available. Please select a location first."
                }
            ),
            400,
        )

    def generate():
        for chunk in query_llm(question, context):
            yield json.dumps(chunk).encode("utf-8")
            sys.stdout.flush()

    return Response(stream_with_context(generate()), mimetype="text/event-stream")


@app.route("/delete_audio", methods=["POST"])
def delete_audio():
    data = request.json
    audio_path = data.get("audio_path")
    if audio_path:
        parsed_url = urlparse(audio_path)
        file_path = os.path.join(os.getcwd(), parsed_url.path[1:])
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return jsonify({"status": "success"}), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        else:
            return jsonify({"error": "File not found"}), 404
    return jsonify({"error": "Invalid path"}), 400


@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename.endswith(".webm"):
        file_format = "webm"
    elif file.filename.endswith(".wav"):
        file_format = "wav"
    else:
        return jsonify({"error": "Unsupported file format"}), 400
    try:
        transcription = transcribe_audio(file, file_format)
        return jsonify({"transcription": transcription})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
