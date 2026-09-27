import os
import uuid

import requests
from flask import Flask, render_template, request, jsonify, url_for
from gtts import gTTS


app = Flask(__name__)


AUDIO_FOLDER = os.path.join(app.static_folder, "audio")
os.makedirs(AUDIO_FOLDER, exist_ok=True)


SUPPORTED_LANGUAGES = {
    "hi": {
        "name": "Hindi",
        "flag": "HI",
        "tts": "hi"
    },
    "es": {
        "name": "Spanish",
        "flag": "ES",
        "tts": "es"
    },
    "fr": {
        "name": "French",
        "flag": "FR",
        "tts": "fr"
    },
    "de": {
        "name": "German",
        "flag": "DE",
        "tts": "de"
    }
}


MYMEMORY_API = "https://api.mymemory.translated.net/get"


def translate_text(text, language):
    if len(text.encode("utf-8")) > 500:
        raise Exception(
            "Text is too long for the translation service. "
            "Please use a shorter sentence."
        )

    params = {
        "q": text,
        "langpair": f"en|{language}",
        "mt": "1"
    }

    email = os.environ.get("MYMEMORY_EMAIL")

    if email:
        params["de"] = email

    response = requests.get(
        MYMEMORY_API,
        params=params,
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    if data.get("responseStatus") != 200:
        raise Exception(
            data.get(
                "responseDetails",
                "Translation service failed."
            )
        )

    response_data = data.get("responseData", {})

    translated_text = response_data.get(
        "translatedText"
    )

    if not translated_text:
        raise Exception(
            "Translation service returned an empty response."
        )

    return translated_text


def generate_audio(text, language):
    filename = f"{uuid.uuid4().hex}.mp3"

    filepath = os.path.join(
        AUDIO_FOLDER,
        filename
    )

    tts_language = SUPPORTED_LANGUAGES[language]["tts"]

    speech = gTTS(
        text=text,
        lang=tts_language,
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

        text = data.get(
            "text",
            ""
        ).strip()

        language = data.get(
            "language",
            ""
        ).strip()

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

        if len(text.encode("utf-8")) > 500:
            return jsonify({
                "success": False,
                "error": "Text is too long. Please enter a shorter text."
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

    except requests.exceptions.Timeout:
        return jsonify({
            "success": False,
            "error": "Translation service timed out. Please try again."
        }), 504

    except requests.exceptions.RequestException as e:
        print("Translation API error:", str(e))

        return jsonify({
            "success": False,
            "error": "Unable to connect to the translation service."
        }), 503

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