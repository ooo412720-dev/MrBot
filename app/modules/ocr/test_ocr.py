from app.modules.ocr.service import (
    extract_text
)

text = extract_text(
    "test.jpg"
)

print(text)