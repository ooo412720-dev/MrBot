# app/modules/ocr/service.py

import pytesseract

from PIL import Image


def extract_text(

        image_path: str

):

    image = Image.open(
        image_path
    )

    text = pytesseract.image_to_string(

        image,

        lang="ara+eng"
    )

    return text.strip()