import os
import uuid

from flask import Flask, render_template, request, jsonify, url_for
from gtts import gTTS
from deep_translator import GoogleTranslator


app = Flask(__name__)


AUDIO_FOLDER = os.path.join(app.static_folder, "audio")
os.makedirs(AUDIO_FOLDER, exist_ok=True)


SUPPORTED_LANGUAGES = {
    "hi": {
        "name": "Hindi",
        "flag": "HI"
    },
    "es": {
        "name": "Spanish",
        "flag": "ES"
    },
    "fr": {
        "name": "French",
        "flag": "FR"
    },
    "de": {
        "name": "German",
        "flag": "DE"
    }
}


def translate_text(text, language):
    translator = GoogleTranslator(
        source="en",
        target=language
    )

    translated_text = translator.translate(text)

    if not translated_text:
        raise Exception("Translation service returned an empty response.")

    return translated_text


def generate_audio(text, language):
    filename = f"{uuid.uuid4().hex}.mp3"

    filepath = os.path.join(
        AUDIO_FOLDER,
        filename
    )

    speech = gTTS(
        text=text,
        lang=language,
        slow=False
    )

    speech.save(filepath)

    return filename


@app.route("/")
def home():
    return render_template(
        "index.html",
        languages=SUPPORTED_LANGUAGES
    )


@app.route("/translate", methods=["POST"])
def translate():
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "success": False,
                "error": "No data received."
            }), 400

        text = data.get("text", "").strip()
        language = data.get("language", "").strip()

        if not text:
            return jsonify({
                "success": False,
                "error": "Please enter some English text."
            }), 400

        if len(text) > 500:
            return jsonify({
                "success": False,
                "error": "Text must be 500 characters or less."
            }), 400

        if language not in SUPPORTED_LANGUAGES:
            return jsonify({
                "success": False,
                "error": "Unsupported target language."
            }), 400

        translated_text = translate_text(
            text,
            language
        )

        filename = generate_audio(
            translated_text,
            language
        )

        audio_url = url_for(
            "static",
            filename=f"audio/{filename}"
        )

        return jsonify({
            "success": True,
            "translated_text": translated_text,
            "language": SUPPORTED_LANGUAGES[language]["name"],
            "audio_url": audio_url
        })

    except Exception as e:

        print("Translation error:", str(e))

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "application": "EchoLang"
    })


if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )
