from pathlib import Path

from app.services.llm_service import llm_service
from app.utils.file_parser import extract_text_from_file

TEXT_EXTENSIONS = {".txt", ".md", ".csv"}
MULTIMODAL_TYPES = {
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}

class DocAgent:
    def parse_document_content(self, raw_text: str) -> str:
        prompt = f"Extract key points, bill amount, due date, or document type from this document text:\n{raw_text}"
        return llm_service.generate_completion(prompt)

    def parse_uploaded_document(self, filename: str, content: bytes) -> str:
        extension = Path(filename).suffix.lower()
        if extension in TEXT_EXTENSIONS:
            text = extract_text_from_file(filename, content)
            if not text.strip():
                raise ValueError("Could not extract text from this file")
            return self.parse_document_content(text)

        mime_type = MULTIMODAL_TYPES.get(extension)
        if mime_type is None:
            raise ValueError("Unsupported file type. Upload a text, PDF, PNG, JPEG, or WebP file.")
        prompt = "Transcribe the document text, then summarize its key points, amounts, and due dates. Do not invent unreadable details."
        return llm_service.generate_document_completion(prompt, content, mime_type)

doc_agent = DocAgent()