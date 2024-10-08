from flask import (
    Flask,
    jsonify,
    request,
    Response,
    render_template,
    session,
    stream_with_context,
    redirect,
    url_for,
)
from services.wikipedia import get_wikipedia_data
from services.llm import query_llm
from services.whisper import transcribe_audio
import json
from dotenv import load_dotenv
import os
from urllib.parse import urlparse
import sys
from services.auth import verify_token
from config import Config
from models import User
from extensions import db
from datetime import datetime, timezone
import secrets

load_dotenv()

app = Flask(__name__)

app.config.from_object(Config)
db.init_app(app)

app.secret_key = os.environ.get("SECRET")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        token_provided = request.form["token"]
        user: User = User.query.filter_by(email=email).first()
        if user and verify_token(user.token, token_provided):
            if datetime.now(timezone.utc) > user.token_expiration:
                error = "Token expired. Please contact support."
                return render_template("login.html", error=error)
            session["user_id"] = user.id
            return redirect(url_for("home"))
        else:
            error = "Invalid email or token."
            return render_template("login.html", error=error)
    return render_template("login.html")


@app.route("/home")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user: User = User.query.filter_by(id=session["user_id"]).first()
    return render_template("index.html", is_admin=user.is_admin)


@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return redirect(url_for("home"))


@app.route("/admin", methods=["GET", "POST"])
def add_user():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user: User = User.query.filter_by(id=session["user_id"]).first()
    if not user.is_admin:
        return "Access denied. Admins only.", 403
    if request.method == "POST":
        email = request.form["email"]
        existing_user: User = User.query.filter_by(email=email).first()
        if existing_user:
            error = "This email is already in use. Please use a different email."
            return render_template("admin.html", error=error)
        token_clear = secrets.token_urlsafe(32)
        new_user = User(email=email)
        new_user.token = User.hash_token(token_clear)
        db.session.add(new_user)
        db.session.commit()
        return render_template("admin.html", token_clear=token_clear, success=True)
    return render_template("admin.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))


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
            data = json.dumps(chunk).encode("utf-8") + b"<|end_of_chunk|>"
            yield data
            sys.stdout.flush()

    return Response(generate(), mimetype="text/event-stream")


@app.route("/llm", methods=["POST"])
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
            data = json.dumps(chunk).encode("utf-8") + b"<|end_of_chunk|>"
            yield data
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
    with app.app_context():
        db.create_all()
        admin_user = User.query.filter_by(is_admin=True).first()
        if not admin_user:
            print("Creating admin user...")
            admin_email = os.environ.get("ADMIN_EMAIL")
            admin_user = User(email=admin_email, is_admin=True, expiration_in_days=365)
            db.session.add(admin_user)
            db.session.commit()

            print(f"Admin user created with email: {admin_email}")
    app.run(debug=True)
