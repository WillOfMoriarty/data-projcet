"""
ocr.py
Google Cloud Vision API integration.
Sends preprocessed image bytes and returns raw text.
"""

import os
import json
from pathlib import Path

# Google Vision SDK
from google.cloud import vision
from google.oauth2 import service_account


def get_vision_client(credentials_path: str = "credentials/google_credentials.json"):
    """
    Build and return an authenticated Vision client.

    Priority:
    1. credentials_path (file)
    2. GOOGLE_APPLICATION_CREDENTIALS env var (auto-picked by SDK)
    3. Raise helpful error

    Usage in Colab:
        client = get_vision_client("/content/my_creds.json")
    """
    abs_path = Path(credentials_path).resolve()

    if abs_path.exists():
        creds = service_account.Credentials.from_service_account_file(
            str(abs_path),
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        return vision.ImageAnnotatorClient(credentials=creds)

    env_creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if env_creds and Path(env_creds).exists():
        return vision.ImageAnnotatorClient()

    raise FileNotFoundError(
        f"No credentials found.\n"
        f"Expected: {abs_path}\n"
        f"Or set env var: GOOGLE_APPLICATION_CREDENTIALS=/path/to/creds.json"
    )


def run_ocr(image_bytes: bytes, client: vision.ImageAnnotatorClient) -> dict:
    """
    Send image bytes to Google Vision API.

    Returns:
        {
            "full_text": "...",       # complete raw OCR text
            "blocks": [...],          # list of text blocks with confidence
            "raw_response": {...}     # full API response (for debugging)
        }
    """
    image = vision.Image(content=image_bytes)

    response = client.document_text_detection(image=image)

    if response.error.message:
        raise RuntimeError(
            f"Google Vision API error: {response.error.message}\n"
            "Check: https://cloud.google.com/apis/design/errors"
        )

    full_text = ""
    blocks = []

    if response.full_text_annotation:
        full_text = response.full_text_annotation.text

        for page in response.full_text_annotation.pages:
            for block in page.blocks:
                block_text = ""
                for paragraph in block.paragraphs:
                    for word in paragraph.words:
                        word_text = "".join(
                            [symbol.text for symbol in word.symbols]
                        )
                        block_text += word_text + " "
                    block_text += "\n"

                blocks.append({
                    "text": block_text.strip(),
                    "confidence": block.confidence,
                    "bounding_box": [
                        {"x": v.x, "y": v.y}
                        for v in block.bounding_box.vertices
                    ]
                })

    return {
        "full_text": full_text,
        "blocks": blocks,
        "raw_response": str(response)  # stringified for JSON serialization
    }


def save_raw_json(ocr_result: dict, output_path: str):
    """Save OCR result as JSON file for debugging/audit trail."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(ocr_result, f, ensure_ascii=False, indent=2)


def load_raw_json(json_path: str) -> dict:
    """Load previously saved OCR result."""
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ── Mock mode (no API key needed for development) ───────────────────────────

MOCK_RECEIPT_TEXT = """INDOMARET
Jl. Pahlawan No.12, Jakarta
Tel: 021-5551234

28/06/2024  14:32:05

AQUA 600ML          2X   3.000    6.000
INDOMIE GORENG      3X   3.500   10.500
TEH BOTOL SOSRO     1X   5.000    5.000
POCARI SWEAT 500ML  2X   7.500   15.000
CHITATO BBQ         1X  12.000   12.000

------------------------------------
SUBTOTAL                    48.500
DISKON MEMBER                2.000
------------------------------------
TOTAL                       46.500

TUNAI                       50.000
KEMBALI                      3.500

Member: 081234567890
Terima kasih atas kunjungan Anda!
"""


def run_ocr_mock() -> dict:
    """
    Returns fake OCR output.
    Use this during development when you don't have a Vision API key yet.

    Usage:
        result = run_ocr_mock()
    """
    return {
        "full_text": MOCK_RECEIPT_TEXT,
        "blocks": [{"text": MOCK_RECEIPT_TEXT, "confidence": 0.99, "bounding_box": []}],
        "raw_response": "MOCK_MODE"
    }
