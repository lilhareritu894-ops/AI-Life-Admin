from pathlib import Path


SUPPORTED_TEXT_EXTENSIONS = {".txt", ".md", ".csv"}


def extract_text_from_file(filename: str, content: bytes) -> str:
    extension = Path(filename).suffix.lower()
    if extension not in SUPPORTED_TEXT_EXTENSIONS:
        raise ValueError("Unsupported file type. Upload a .txt, .md, or .csv file.")
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("File must contain valid UTF-8 text.") from exc