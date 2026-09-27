# EchoLang – Multilingual Text-to-Speech

EchoLang is a lightweight web-based multilingual text-to-speech application built using Python and Flask.

It allows users to enter English text, select a target language, translate the text using the MyMemory Translation API, and convert the translated text into speech using Google Text-to-Speech (gTTS).

## Features

- English to multilingual translation
- Hindi, Spanish, French and German support
- Text-to-speech generation
- Browser-based audio playback
- Responsive and mobile-friendly UI
- Input validation and error handling
- Lightweight Flask backend
- GitHub and Render deployment support

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, Flask
- **Translation:** MyMemory Translation API
- **Text-to-Speech:** gTTS
- **Production Server:** Gunicorn
- **Deployment:** Render
- **Version Control:** Git & GitHub

## Project Structure

```text
EchoLang/
│
├── static/
│   └── audio/
│       └── generated MP3 files
│
├── templates/
│   └── index.html
│
├── app.py
├── requirements.txt
├── .python-version
├── .gitignore
└── README.md

## Overview

EchoLang combines **machine translation** and **text-to-speech technology** into a single web application.

The application follows this workflow:

```text
User enters English text
        ↓
Selects target language
        ↓
Translation API
        ↓
Translated text
        ↓
Google Text-to-Speech (gTTS)
        ↓
Generated MP3 audio
        ↓
Audio playback in browser