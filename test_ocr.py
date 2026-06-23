import pytesseract
from PIL import Image

image = Image.open("boot.jpg")

text = pytesseract.image_to_string(
    image,
    lang="ara+eng"
)

print(text)