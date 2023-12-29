"""
This is the entrypoint for the BeReal server.

It contains the Flask app routing and the functions to interact with the BeReal API.
"""
import os
from typing import Any

from flask import Flask, Response, abort, jsonify, request, send_from_directory
from flask_cors import CORS
from itsdangerous import SignatureExpired, URLSafeTimedSerializer

from .bereal import memories, send_code, verify_code
from .images import cleanup_images, create_images
from .logger import logger
from .utils import CONTENT_PATH, EXPORTS_PATH, FLASK_ENV, GIT_COMMIT_HASH, HOST, PORT, SECRET_KEY, str2mode, year2dates
from .videos import build_slideshow

app = Flask(__name__)
serializer = URLSafeTimedSerializer(SECRET_KEY)

if FLASK_ENV == "development":
    CORS(app)
else:
    CORS(app, resources={r"/*": {"origins": "https://michaeldemar.co"}})

# TODO(michaelfromyeg): make this a database
PHONE_TO_TOKEN: dict[str, str] = {}


@app.route("/status")
def status() -> Response:
    """
    Return the status of the server.
    """
    return jsonify({"status": "ok", "version": GIT_COMMIT_HASH})


@app.route("/request-otp", methods=["POST"])
def request_otp() -> tuple[Response, int]:
    """
    Request an OTP code for a user.
    """
    data: dict[str, Any] = request.get_json()
    phone = data["phone"]

    otp_session = send_code(f"+{phone}")

    if otp_session is None:
        return jsonify({"error": "Invalid phone number"}), 400

    return jsonify({"otpSession": otp_session}), 200


@app.route("/validate-otp", methods=["POST"])
def validate_otp() -> tuple[Response, int]:
    """
    Validate the user's input and render the process page.
    """
    data: dict[str, Any] = request.get_json()
    phone = data["phone"]
    otp_session = data["otp_session"]

    otp_code = data["otp_code"]

    token = verify_code(otp_session, otp_code)

    if token is None:
        return jsonify({"error": "Invalid verification code"}), 400

    PHONE_TO_TOKEN[phone] = token

    return jsonify({"token": token}), 200


@app.route("/video", methods=["POST"])
def create_video() -> tuple[Response, int]:
    """
    Process a user's input and render the preview page.
    """
    phone = request.form["phone"]
    token = request.form["token"]
    short_token = token[:10]

    if phone not in PHONE_TO_TOKEN or PHONE_TO_TOKEN[phone] != token:
        return jsonify({"error": "Invalid token"}), 400

    year = request.form["year"]
    sdate, edate = year2dates(year)

    wav_file = request.files["file"]

    mode_str = request.form.get("mode")
    mode = str2mode(mode_str)

    logger.debug("Downloading music file %s...", wav_file.filename)

    song_folder = os.path.join(CONTENT_PATH, phone, year)
    os.makedirs(song_folder, exist_ok=True)
    song_path = os.path.join(song_folder, "song.wav")

    try:
        wav_file.save(song_path)
    except Exception as error:
        logger.warning("Could not save music file, received: %s", error)

    logger.debug("Downloading images locally...")
    result = memories(phone, year, token, sdate, edate)

    if not result:
        return jsonify({"error": "Could not generate images; try again later"}), 500

    video_file = f"{short_token}-{phone}-{year}.mp4"

    image_folder = create_images(phone, year)
    build_slideshow(image_folder, song_path, video_file, mode)
    cleanup_images(phone, year)

    return jsonify({"videoUrl": video_file}), 200


@app.route("/video/<filename>", methods=["GET"])
def get_video(filename: str) -> tuple[Response, int]:
    """
    Serve a video file.
    """
    try:
        return send_from_directory(EXPORTS_PATH, filename, mimetype="video/mp4"), 200
    except SignatureExpired:
        # TODO(michaelfromyeg): implement this
        abort(403)


@app.errorhandler(500)
def internal_error(error) -> Response:
    logger.error("Got 500 error: %s", error)

    response = jsonify({"error": "Internal Server Error", "message": "An internal server error occurred"})
    response.status_code = 500
    return response


if __name__ == "__main__":
    OS_HOST: str | None = os.environ.get("HOST")
    OS_PORT: str | None = os.environ.get("PORT")

    host = OS_HOST or HOST or "localhost"
    port = OS_PORT or PORT or 5000
    port = int(port)

    logger.info("Starting BeReal server on %s:%d...", host, port)

    app.run(host=host, port=port, debug=True)
