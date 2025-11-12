"""
Parser Core Module
Contains field extraction, mapping, and promotion logic.
"""
from .field_extractor import FieldExtractor
from .store_and_promote import save_to_neon, save_to_firebase, trigger_n8n_webhook

__all__ = [
    "FieldExtractor",
    "save_to_neon",
    "save_to_firebase",
    "trigger_n8n_webhook",
]
