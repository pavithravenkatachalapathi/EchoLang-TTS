import os
import gc
import uuid

import torch
from flask import Flask, render_template, request, jsonify, url_for
from gtts import gTTS
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


os.environ["TOKENIZERS_PARALLELISM"] = "false"
torch.set_num_threads(1)


app = Flask(__name__)


AUDIO_FOLDER = os.path.join(
    app.static_folder,
    "audio"
)

os.makedirs(
    AUDIO_FOLDER,
    exist_ok=True
)


SUPPORTED_LANGUAGES = {
    "hi": {
        "name": "Hindi",
        "flag": "HI",
        "tts": "hi",
        "model": "Helsinki-NLP/opus-mt-en-hi"
    },
    "es": {
        "name": "Spanish",
        "flag": "ES",
        "tts": "es",
        "model": "Helsinki-NLP/opus-mt-en-es"
    },
    "fr": {
        "name": "French",
        "flag": "FR",
        "tts": "fr",
        "model": "Helsinki-NLP/opus-mt-en-fr"
    },
    "de": {
        "name": "German",
        "flag": "DE",
        "tts": "de",
        "model": "Helsinki-NLP/opus-mt-en-de"
    }
}


CURRENT_LANGUAGE = None
CURRENT_TOKENIZER = None
CURRENT_MODEL = None


def load_model(language):

    global CURRENT_LANGUAGE
    global CURRENT_TOKENIZER
    global CURRENT_MODEL

    if (
        CURRENT_LANGUAGE == language
        and CURRENT_TOKENIZER is not None
        and CURRENT_MODEL is not None
    ):
        return CURRENT_TOKENIZER, CURRENT_MODEL

    if CURRENT_MODEL is not None:
        del CURRENT_MODEL
        CURRENT_MODEL = None

    if CURRENT_TOKENIZER is not None:
        del CURRENT_TOKENIZER
        CURRENT_TOKENIZER = None

    gc.collect()

    if hasattr(torch, "cuda") and torch.cuda.is_available():
        torch.cuda.empty_cache()

    model_name = SUPPORTED_LANGUAGES[
        language
    ]["model"]

    print(
        f"Loading translation model: {model_name}"
    )

    tokenizer = AutoTokenizer.from_pretrained(
        model_name
    )

    model = AutoModelForSeq2SeqLM.from_pretrained(
        model_name
    )

    model.eval()

    CURRENT_LANGUAGE = language
    CURRENT_TOKENIZER = tokenizer
    CURRENT_MODEL = model

    print(
        f"Model loaded successfully: {model_name}"
    )

    return tokenizer, model


def translate_text(text, language):

    tokenizer, model = load_model(
        language
    )

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=128
    )

    with torch.no_grad():

        outputs = model.generate(
            **inputs,
            max_length=128,
            num_beams=1,
            do_sample=False
        )

    translated_text = tokenizer.decode(
        outputs[0],
        skip_special_tokens=True
    )

    if not translated_text:
        raise Exception(
            "Translation model returned empty text."
        )

    return translated_text


def generate_audio(text, language):

    filename = (
        f"{uuid.uuid4().hex}.mp3"
    )

    filepath = os.path.join(
        AUDIO_FOLDER,
        filename
    )

    tts_language = SUPPORTED_LANGUAGES[
        language
    ]["tts"]

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


@app.route(
    "/translate",
    methods=["POST"]
)
def translate():

    try:

        data = request.get_json(
            silent=True
        )

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
                "error":
                    "Please enter some English text."
            }), 400

        if len(text) > 500:

            return jsonify({
                "success": False,
                "error":
                    "Text must be 500 characters or less."
            }), 400

        if language not in SUPPORTED_LANGUAGES:

            return jsonify({
                "success": False,
                "error":
                    "Unsupported target language."
            }), 400

        print(
            f"Translation requested: "
            f"{language}"
        )

        translated_text = translate_text(
            text,
            language
        )

        print(
            f"Translation completed: "
            f"{translated_text}"
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

            "translated_text":
                translated_text,

            "language":
                SUPPORTED_LANGUAGES[
                    language
                ]["name"],

            "audio_url":
                audio_url
        })

    except Exception as e:

        print(
            "Translation error:",
            str(e)
        )

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/health")
def health():

    return jsonify({
        "status": "ok",
        "application": "EchoLang",
        "translation": "MarianMT"
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