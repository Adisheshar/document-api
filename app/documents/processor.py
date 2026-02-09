"""
app/documents/processor.py

This module contains isolated, synchronous document processing logic.
It simulates OCR/parsing/analysis without depending on FastAPI or database layers.

Design goals:
- No framework or DB dependencies
- Deterministic, testable core logic
- Clear failure signaling via exceptions
- Reusable across services, workers, or CLI tools
"""

import os
import time
import random
from typing import Dict


class DocumentProcessingError(Exception):
    """
    Raised when document processing fails.
    This is intentionally generic so the service layer
    can decide how to handle or map it.
    """
    pass


def process_document(file_path: str, filename: str) -> Dict[str, object]:
    """
    Simulate processing of a document (OCR / parsing / analysis).

    This function is synchronous and blocking by design.
    It should be called from the service layer, not directly from API routes.

    Parameters:
        file_path (str): Absolute or relative path to the file on disk
        filename (str): Original filename (used for metadata simulation)

    Returns:
        dict: Structured processing result:
            {
                "text": str,
                "pages": int,
                "language": str,
                "confidence": float
            }

    Raises:
        FileNotFoundError:
            If the file path does not exist
        DocumentProcessingError:
            If simulated processing fails
    """

    # --- Basic validation ---
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found at path: {file_path}")

    # --- Simulate processing delay ---
    # Represents OCR / parsing / ML inference time
    processing_time = random.uniform(0.5, 1.5)
    time.sleep(processing_time)

    # --- Simulate random failure (low probability) ---
    # ~5% chance of failure
    if random.random() < 0.05:
        raise DocumentProcessingError(
            f"Failed to process document '{filename}' due to simulated error"
        )

    # --- Simulated extraction logic ---
    # These values are intentionally fake but structured
    pages = random.randint(1, 10)

    extracted_text = (
        f"Simulated extracted text from '{filename}'. "
        f"This document contains {pages} page(s)."
    )

    # Language detection simulation (simple heuristic)
    language = "en"

    # Confidence score (simulated OCR confidence)
    confidence = round(random.uniform(0.90, 0.99), 2)

    # --- Processing result ---
    result = {
        "text": extracted_text,
        "pages": pages,
        "language": language,
        "confidence": confidence,
    }

    return result
