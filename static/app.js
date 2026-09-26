const inputText = document.getElementById("inputText");
const characterCount = document.getElementById("characterCount");

const languageSelect = document.getElementById("languageSelect");

const translateButton = document.getElementById("translateButton");
const buttonText = document.getElementById("buttonText");

const loadingState = document.getElementById("loadingState");

const outputSection = document.getElementById("outputSection");
const translatedText = document.getElementById("translatedText");
const outputLanguage = document.getElementById("outputLanguage");

const audioPlayer = document.getElementById("audioPlayer");

const errorMessage = document.getElementById("errorMessage");

const copyButton = document.getElementById("copyButton");


/* CHARACTER COUNT */

inputText.addEventListener("input", () => {

    const length = inputText.value.length;

    characterCount.textContent = `${length} / 500`;

});


/* TRANSLATE */

translateButton.addEventListener("click", async () => {

    const text = inputText.value.trim();

    const language = languageSelect.value;


    if (!text) {

        showError("Please enter some English text first.");

        inputText.focus();

        return;
    }


    hideError();

    outputSection.classList.add("hidden");

    loadingState.classList.remove("hidden");

    translateButton.disabled = true;

    buttonText.textContent = "Processing...";


    try {

        const response = await fetch("/translate", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                text: text,
                language: language
            })

        });


        const data = await response.json();


        if (!response.ok || !data.success) {

            throw new Error(
                data.error || "Something went wrong."
            );

        }


        translatedText.textContent =
            data.translated_text;

        outputLanguage.textContent =
            data.language;


        audioPlayer.src =
            data.audio_url;

        audioPlayer.load();


        outputSection.classList.remove("hidden");


        outputSection.scrollIntoView({
            behavior: "smooth",
            block: "nearest"
        });


    } catch (error) {

        showError(
            error.message ||
            "Unable to process your request."
        );

    } finally {

        loadingState.classList.add("hidden");

        translateButton.disabled = false;

        buttonText.textContent =
            "Translate & Speak";

    }

});


/* COPY */

copyButton.addEventListener("click", async () => {

    const text =
        translatedText.textContent.trim();


    if (!text) {
        return;
    }


    try {

        await navigator.clipboard.writeText(text);

        const original =
            copyButton.textContent;

        copyButton.textContent = "✓";

        setTimeout(() => {

            copyButton.textContent =
                original;

        }, 1500);

    } catch (error) {

        showError(
            "Unable to copy the translation."
        );

    }

});


/* ERROR */

function showError(message) {

    errorMessage.textContent = message;

    errorMessage.classList.remove("hidden");

}


function hideError() {

    errorMessage.classList.add("hidden");

    errorMessage.textContent = "";

}


/* ENTER KEY */

inputText.addEventListener("keydown", (event) => {

    if (
        event.key === "Enter" &&
        event.ctrlKey
    ) {

        translateButton.click();

    }

});