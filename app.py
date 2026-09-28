import os
import uuid
import gc

import torch
from flask import Flask, render_template, request, jsonify, url_for
from gtts import gTTS
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


app = Flask(__name__)

torch.set_num_threads(1)
torch.set_num_interop_threads(1)


AUDIO_FOLDER = os.path.join(app.static_folder, "audio")
os.makedirs(AUDIO_FOLDER, exist_ok=True)


SUPPORTED_LANGUAGES = {
    "hi": {
        "name": "Hindi",
        "flag": "HI",
        "model": "Helsinki-NLP/opus-mt-en-hi",
        "tts": "hi"
    },
    "es": {
        "name": "Spanish",
        "flag": "ES",
        "model": "Helsinki-NLP/opus-mt-en-es",
        "tts": "es"
    },
    "fr": {
        "name": "French",
        "flag": "FR",
        "model": "Helsinki-NLP/opus-mt-en-fr",
        "tts": "fr"
    },
    "de": {
        "name": "German",
        "flag": "DE",
        "model": "Helsinki-NLP/opus-mt-en-de",
        "tts": "de"
    }
}


def translate_text(text, language):

    model_name = SUPPORTED_LANGUAGES[language]["model"]

    tokenizer = None
    model = None

    try:

        tokenizer = AutoTokenizer.from_pretrained(
            model_name
        )

        model = AutoModelForSeq2SeqLM.from_pretrained(
            model_name
        )

        model.eval()

        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=256
        )

        with torch.inference_mode():

            outputs = model.generate(
                **inputs,
                max_length=256,
                num_beams=2,
                early_stopping=True
            )

        translated_text = tokenizer.decode(
            outputs[0],
            skip_special_tokens=True
        )

        return translated_text

    finally:

        del model
        del tokenizer
        gc.collect()

        if torch.cuda.is_available():
            torch.cuda.empty_cache()


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

        print(
            "Translation error:",
            str(e)
        )

        return jsonify({
            "success": False,
            "error": "Translation failed. Please try again."
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
        debug=False
    )