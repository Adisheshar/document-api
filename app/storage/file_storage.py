#app/storage/file storage
from pathlib import Path
from uuid import uuid4

from app.core import config


class LocalFileStorage:
    """
    Local filesystem-based file storage.
    Decoupled from FastAPI and database layers.
    """

    ALLOWED_EXTENSIONS = {".pdf", ".docx"}

    def __init__(self) -> None:
        self.upload_dir = Path(config.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def save_file(self, filename: str, file_bytes: bytes) -> str:
        """
        Save raw file bytes to disk with a unique filename.
        Returns the file path as string.
        """
        extension = Path(filename).suffix.lower()

        if extension not in self.ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Invalid file type '{extension}'. "
                f"Allowed types: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )

        unique_name = f"{uuid4().hex}{extension}"
        file_path = self.upload_dir / unique_name

        with file_path.open("wb") as f:
            f.write(file_bytes)

        return str(file_path)
