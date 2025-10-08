# app.py
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
import io
import cv2
import numpy as np
from spellchecker import SpellChecker
from paddleocr import PaddleOCR # Import PaddleOCR

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LANGUAGE_SCRIPTS = {
    'pan': sanscript.GURMUKHI,
    'hi': sanscript.DEVANAGARI,  # Tesseract uses 'hin', PaddleOCR uses 'hi'
    'ben': sanscript.BENGALI,
    'mar': sanscript.DEVANAGARI,
    'ta': sanscript.TAMIL,     # Tesseract uses 'tam', PaddleOCR uses 'ta'
    'te': sanscript.TELUGU,     # Tesseract uses 'tel', PaddleOCR uses 'te'
    'kan': sanscript.KANNADA,
    'guj': sanscript.GUJARATI,
    'ma': sanscript.MALAYALAM, # Tesseract uses 'mal', PaddleOCR uses 'ma'
}

# --- Initialize the PaddleOCR model ---
# This will download the models the first time it's run
ocr = PaddleOCR(use_angle_cls=True, lang='en')
# ------------------------------------

def correct_spellings(text):
    # (This function remains unchanged)
    spell = SpellChecker()
    corrected_words = []
    # (Rest of function is the same)
    # ...
    return " ".join(corrected_words)

@app.post("/process-image/")
async def process_image(
    image: UploadFile = File(...),
    language: str = Form("pan"),
    target_script: str = Form("ITRANS")
):
    contents = await image.read()
    
    nparr = np.frombuffer(contents, np.uint8)
    img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # --- NEW: Use PaddleOCR for text extraction ---
    # Update the language code for PaddleOCR
    paddle_lang_code = language
    if language == 'hin': paddle_lang_code = 'hi'
    elif language == 'tam': paddle_lang_code = 'ta'
    elif language == 'tel': paddle_lang_code = 'te'
    elif language == 'mal': paddle_lang_code = 'ma'
    
    ocr.lang = paddle_lang_code # Set the language for the current request
    
    result = ocr.ocr(img_cv, cls=True)
    
    extracted_text = ""
    if result and result[0] is not None:
        # Extract text from PaddleOCR's complex output
        text_lines = [line[1][0] for line in result[0]]
        extracted_text = "\n".join(text_lines)
    # ---------------------------------------------

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
