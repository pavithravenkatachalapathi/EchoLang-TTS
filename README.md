# EchoLang – Multilingual Text-to-Speech

EchoLang is a web-based multilingual text-to-speech application that converts English text into multiple languages and generates natural-sounding speech for the translated text.

The application provides a simple and professional interface where users can enter English text, select a target language, translate the content, and listen to the translated speech directly from the browser.

---

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