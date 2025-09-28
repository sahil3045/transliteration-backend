# main.py
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import pytesseract
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
import io
import cv2
import numpy as np
from spellchecker import SpellChecker

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- NEW: Dictionary to map language codes to scripts ---
# This makes adding new languages very easy
LANGUAGE_SCRIPTS = {
    'pan': sanscript.GURMUKHI,
    'hin': sanscript.DEVANAGARI,
    'ben': sanscript.BENGALI,
    'mar': sanscript.DEVANAGARI,  # Marathi uses Devanagari
    'tam': sanscript.TAMIL,
    'tel': sanscript.TELUGU,
    'kan': sanscript.KANNADA,
    'guj': sanscript.GUJARATI,
    'mal': sanscript.MALAYALAM,
}
# ---------------------------------------------------------

def correct_spellings(text):
    # (This function remains unchanged)
    spell = SpellChecker()
    corrected_words = []
    words = text.split()
    misspelled = spell.unknown(words)
    for word in words:
        if word in misspelled:
            correction = spell.correction(word)
            if correction:
                corrected_words.append(correction)
            else:
                corrected_words.append(word)
        else:
            corrected_words.append(word)
    return " ".join(corrected_words)

@app.post("/process-image/")
async def process_image(
    image: UploadFile = File(...),
    language: str = Form("pan"),
    target_script: str = Form("ITRANS") # <-- ADD THIS LINE
):
    contents = await image.read()

    nparr = np.frombuffer(contents, np.uint8)
    img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    gray_img = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    _, threshold_img = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    pil_img = Image.fromarray(threshold_img)

    tesseract_langs = f'{language}+eng'
    extracted_text = pytesseract.image_to_string(pil_img, lang=tesseract_langs)

    if target_script == "ITRANS":
        extracted_text = correct_spellings(extracted_text)

    source_script = LANGUAGE_SCRIPTS.get(language, sanscript.DEVANAGARI)

    target_scheme = getattr(sanscript, target_script.upper())
    transliterated_text = transliterate(extracted_text, source_script, target_scheme)

    return {
        "original_text": extracted_text,
        "transliterated_text": transliterated_text
    }
#conda activate ocr_env
#uvicorn main:app --reload --host 0.0.0.0
