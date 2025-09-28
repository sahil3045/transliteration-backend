# test_ocr.py (Updated Example)
import pytesseract
from PIL import Image
from indic_transliteration import sanscript
from indic_transliteration.sanscript import SchemeMap, SCHEMES, transliterate

IMAGE_PATH = 'your_image_name.jpg'
LANGUAGES = 'pan+eng' # Punjabi + English

try:
    print(f"Running Tesseract OCR on {IMAGE_PATH}...")
    img = Image.open(IMAGE_PATH)
    extracted_text = pytesseract.image_to_string(img, lang=LANGUAGES)

    print("\n--- OCR Result (Original Script) ---")
    print(extracted_text)
    print("------------------------------------")

    # --- NEW TRANSLITERATION STEP ---
    print("\n--- Transliterated Result (to English/Latin) ---")
    # Transliterate from Gurmukhi to ITRANS (a Latin/English representation)
    transliterated_text = transliterate(extracted_text, sanscript.GURMUKHI, sanscript.ITRANS)
    print(transliterated_text)
    print("-------------------------------------------------")

except Exception as e:
    print(f"An error occurred: {e}")