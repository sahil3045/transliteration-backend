# check.py
from easyocr import easyocr

print("Checking supported languages in this EasyOCR installation...")
print(sorted(easyocr.all_lang_list))