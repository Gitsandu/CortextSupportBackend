import easyocr
import requests
from PIL import Image
from io import BytesIO
import logging

# Configure logging to only show ERROR-level logs
logging.getLogger().setLevel(logging.ERROR)
logging.getLogger("easyocr").setLevel(logging.ERROR)

# Lowercase error keywords for case-insensitive matching
error_keywords = [kw.lower() for kw in [
    "error", "exception", "invalid", "failed", "not found", "unable", "denied", "timeout", "crash", "missing",
    "forbidden", "unavailable", "unauthorized", "disconnect", "refused", "rejected", "not allowed", "cannot",
    "bug", "conflict", "does not exist", "corrupt", "broken", "null", "undefined", "stack trace", "traceback",
    "syntax error", "runtime error", "type error", "connection lost", "network error", "file not found",
    "disk full", "no such file", "read-only", "unknown", "out of memory", "segmentation fault", "panic",
    "unexpected", "fatal", "abort", "terminated", "incomplete", "overflow", "underflow", "server error",
    "internal server", "503", "500", "404", "403", "bad request", "unprocessable", "malformed", "invalid input",
    "authentication failed", "login failed", "password incorrect", "resource busy", "conflicting update",
    "not implemented", "deprecated", "cannot connect", "connection error", "bad gateway", "gateway timeout",
    "something went wrong", "try again later", "please try again"
]]

try:
    image_url = 'https://global.discourse-cdn.com/auth0/original/3X/e/3/e34087415bf29533233d4ba452b40a49b84b3283.jpeg'
    response = requests.get(image_url)
    response.raise_for_status()

    image = Image.open(BytesIO(response.content))
    image.save("temp_image.png")

    reader = easyocr.Reader(['en'])
    results = reader.readtext("temp_image.png")

    print("🔍 Detected Error Lines:")
    found = False
    for bbox, text, confidence in results:
        lower_text = text.lower()
        if any(keyword in lower_text for keyword in error_keywords):
            print(f"❌ {text} (Confidence: {confidence:.2f})")
            found = True

    if not found:
        print("✅ No error-related text found in the screenshot.")

except Exception as e:
    logging.error("An error occurred during OCR processing", exc_info=True)
