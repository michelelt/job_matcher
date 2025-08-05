import os
from typing import Set
import configparser

# Per DOCX
try:
    from docx import Document
except ImportError:  # fallback semplice se manca python-docx
    Document = None

# Per immagini / OCR
try:
    from PIL import Image, ImageSequence
    import pytesseract
except ImportError:
    Image = None
    ImageSequence = None
    pytesseract = None

def _ensure_ocr_available():
    if Image is None or pytesseract is None:
        raise RuntimeError(
            "Dipendenze mancanti per OCR. Installa pillow e pytesseract: "
            "pip install pillow pytesseract"
        )
    # opzionale: controlla che tesseract sia installato nel sistema
    try:
        pytesseract.get_tesseract_version()
    except Exception as e:
        raise RuntimeError(
            "Tesseract non sembra installato o non è raggiungibile. "
            "Installa tesseract (es. su Ubuntu: sudo apt install tesseract-ocr) "
            f"Errore interno: {e}"
        )

def image_to_plain_text(path: str) -> str:
    """
    OCR su immagini: .jpeg, .jpg, .png, .webp, e .gif (animata -> frame multipli).
    """
    _ensure_ocr_available()
    if not os.path.isfile(path):
        raise FileNotFoundError(f"File non trovato: {path}")
    try:
        img = Image.open(path)
    except Exception as e:
        raise RuntimeError(f"Impossibile aprire l'immagine: {e}")

    texts = []
    if getattr(img, "is_animated", False):
        # GIF animata: OCR su ogni frame, unisci evitando ripetizioni banali
        seen = set()
        for frame in ImageSequence.Iterator(img):
            frame = frame.convert("RGB")
            txt = pytesseract.image_to_string(frame)
            norm = txt.strip()
            if norm and norm not in seen:
                seen.add(norm)
                texts.append(norm)
    else:
        # singola immagine
        img = img.convert("RGB")
        txt = pytesseract.image_to_string(img)
        texts.append(txt.strip())

    return "\n\n".join(t for t in texts if t)

def docx_to_plain_text(path: str) -> str:
    """
    Estrae testo da .docx.
    """
    if Document is None:
        raise RuntimeError("Serve python-docx: pip install python-docx")
    if not os.path.isfile(path):
        raise FileNotFoundError(f"File non trovato: {path}")
    try:
        doc = Document(path)
    except Exception as e:
        raise RuntimeError(f"Impossibile aprire .docx: {e}")
    paragraphs = [p.text for p in doc.paragraphs if p.text]
    return "\n".join(paragraphs)

def ini_to_plain_text(path: str) -> str:
    """
    Converte .ini in una rappresentazione testuale piatta (sezioni e chiavi=valore).
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"File non trovato: {path}")
    config = configparser.ConfigParser()
    config.read(path, encoding="utf-8")
    output_lines = []
    for section in config.sections():
        output_lines.append(f"[{section}]")
        for key, val in config.items(section):
            output_lines.append(f"{key} = {val}")
        output_lines.append("")  # separatore
    return "\n".join(output_lines).strip()

# Mappatura estensioni -> funzione
EXTENSION_HANDLERS = {
    "jpeg": image_to_plain_text,
    "jpg": image_to_plain_text,
    "png": image_to_plain_text,
    "webp": image_to_plain_text,
    "gif": image_to_plain_text,
    "docx": docx_to_plain_text,
    "ini": ini_to_plain_text,
}

def file_to_plain_text(path: str) -> str:
    """
    Dispatch generico: usa l'estensione del file per chiamare la funzione corretta.
    """
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    if ext not in EXTENSION_HANDLERS:
        raise ValueError(f"Estensione non supportata: {ext}")
    handler = EXTENSION_HANDLERS[ext]
    return handler(path)
