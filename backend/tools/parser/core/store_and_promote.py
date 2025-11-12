"""
Store and Promote Module
Saves extracted fields to Neon/Firebase and triggers n8n webhooks
"""

import os
import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import asyncpg
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


# Configuration from environment
NEON_URL = os.getenv("NEON_URL", "")
N8N_DOC_WEBHOOK_URL = os.getenv("N8N_DOC_WEBHOOK_URL", "")
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS", "")


async def save_to_neon(
    fields: List[Dict[str, Any]],
    metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Save extracted fields to Neon database

    Args:
        fields: List of extracted field dictionaries
        metadata: Document metadata including doc_id, filename, document_type, etc.

    Returns:
        Dictionary with success status and inserted count

    Table Schema:
        CREATE TABLE doc_parser_fillable (
            doc_id UUID,
            filename TEXT,
            field_name TEXT,
            field_value TEXT,
            matched_field TEXT,
            confidence NUMERIC,
            source_text TEXT,
            document_type TEXT,
            parsed_at TIMESTAMPTZ DEFAULT now()
        );
    """

    if not NEON_URL:
        logger.error("NEON_URL not configured in environment")
        raise ValueError("NEON_URL not configured. Please set it in .env file.")

    # Extract metadata
    doc_id = metadata.get('doc_id')
    if not doc_id:
        doc_id = str(uuid.uuid4())
        logger.info(f"Generated new doc_id: {doc_id}")

    filename = metadata.get('filename', 'unknown')
    document_type = metadata.get('document_type', 'unknown')
    source_text = metadata.get('source_text', '')

    logger.info(f"Saving {len(fields)} fields to Neon for doc_id: {doc_id}")

    try:
        # Connect to Neon database
        conn = await asyncpg.connect(NEON_URL)

        try:
            # Prepare insert query
            insert_query = """
                INSERT INTO doc_parser_fillable (
                    doc_id, filename, field_name, field_value,
                    matched_field, confidence, source_text, document_type, parsed_at
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """

            # Insert each field
            inserted_count = 0
            for field in fields:
                field_name = field.get('label', '')
                field_value = field.get('value', '')
                matched_field = field.get('matched_field', '')
                confidence = field.get('confidence', 0.0)

                await conn.execute(
                    insert_query,
                    doc_id,
                    filename,
                    field_name,
                    field_value,
                    matched_field,
                    confidence,
                    source_text[:1000] if source_text else '',  # Truncate if too long
                    document_type,
                    datetime.utcnow()
                )
                inserted_count += 1

            logger.info(f"Successfully inserted {inserted_count} fields to Neon")

            return {
                "success": True,
                "destination": "neon",
                "doc_id": doc_id,
                "inserted_count": inserted_count,
                "message": f"Saved {inserted_count} fields to Neon database"
            }

        finally:
            await conn.close()

    except asyncpg.exceptions.UndefinedTableError:
        logger.error("Table 'doc_parser_fillable' does not exist. Please create it first.")
        raise ValueError(
            "Table 'doc_parser_fillable' not found. "
            "Run the SQL schema creation script first."
        )
    except Exception as e:
        logger.error(f"Failed to save to Neon: {e}", exc_info=True)
        raise


async def trigger_n8n_webhook(
    doc_id: str,
    fields: List[Dict[str, Any]],
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Trigger n8n webhook with extracted fields

    Args:
        doc_id: Document UUID
        fields: List of extracted field dictionaries
        metadata: Optional additional metadata

    Returns:
        Dictionary with webhook response status

    Webhook Payload:
        {
            "doc_id": "uuid",
            "fields": [...],
            "metadata": {...},
            "timestamp": "ISO timestamp"
        }
    """

    if not N8N_DOC_WEBHOOK_URL:
        logger.error("N8N_DOC_WEBHOOK_URL not configured in environment")
        raise ValueError("N8N_DOC_WEBHOOK_URL not configured. Please set it in .env file.")

    logger.info(f"Triggering n8n webhook for doc_id: {doc_id}")

    # Prepare webhook payload
    payload = {
        "doc_id": doc_id,
        "fields": fields,
        "field_count": len(fields),
        "high_confidence_count": len([f for f in fields if f.get('confidence', 0) >= 0.8]),
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Add metadata if provided
    if metadata:
        payload["metadata"] = metadata

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                N8N_DOC_WEBHOOK_URL,
                json=payload,
                headers={"Content-Type": "application/json"}
            )

            response.raise_for_status()

            logger.info(f"n8n webhook triggered successfully: {response.status_code}")

            return {
                "success": True,
                "destination": "n8n",
                "doc_id": doc_id,
                "status_code": response.status_code,
                "webhook_url": N8N_DOC_WEBHOOK_URL,
                "message": "Successfully triggered n8n webhook"
            }

    except httpx.HTTPStatusError as e:
        logger.error(f"n8n webhook failed with status {e.response.status_code}: {e}")
        raise ValueError(f"n8n webhook failed: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to n8n webhook: {e}")
        raise ValueError(f"Failed to connect to n8n webhook: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error triggering n8n webhook: {e}", exc_info=True)
        raise


async def save_to_firebase(
    fields: List[Dict[str, Any]],
    metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Save extracted fields to Firebase Firestore

    Args:
        fields: List of extracted field dictionaries
        metadata: Document metadata including doc_id, filename, document_type, etc.

    Returns:
        Dictionary with success status and document ID

    Note:
        Requires firebase-admin to be installed and FIREBASE_CREDENTIALS to be configured
    """

    if not FIREBASE_CREDENTIALS:
        logger.error("FIREBASE_CREDENTIALS not configured in environment")
        raise ValueError(
            "FIREBASE_CREDENTIALS not configured. "
            "Please set it in .env file with path to Firebase credentials JSON."
        )

    try:
        # Import Firebase Admin (optional dependency)
        try:
            import firebase_admin
            from firebase_admin import credentials, firestore
        except ImportError:
            raise ImportError(
                "Firebase Admin SDK not installed. "
                "Install with: pip install firebase-admin"
            )

        # Extract metadata
        doc_id = metadata.get('doc_id')
        if not doc_id:
            doc_id = str(uuid.uuid4())

        filename = metadata.get('filename', 'unknown')
        document_type = metadata.get('document_type', 'unknown')

        logger.info(f"Saving {len(fields)} fields to Firebase for doc_id: {doc_id}")

        # Initialize Firebase if not already initialized
        if not firebase_admin._apps:
            cred = credentials.Certificate(FIREBASE_CREDENTIALS)
            firebase_admin.initialize_app(cred)

        # Get Firestore client
        db = firestore.client()

        # Prepare document data
        doc_data = {
            "doc_id": doc_id,
            "filename": filename,
            "document_type": document_type,
            "fields": fields,
            "field_count": len(fields),
            "high_confidence_count": len([f for f in fields if f.get('confidence', 0) >= 0.8]),
            "parsed_at": firestore.SERVER_TIMESTAMP,
            "metadata": metadata
        }

        # Save to Firestore collection
        doc_ref = db.collection('doc_parser_fillable').document(doc_id)
        doc_ref.set(doc_data)

        logger.info(f"Successfully saved to Firebase: {doc_id}")

        return {
            "success": True,
            "destination": "firebase",
            "doc_id": doc_id,
            "document_ref": f"doc_parser_fillable/{doc_id}",
            "inserted_count": len(fields),
            "message": f"Saved document to Firebase with {len(fields)} fields"
        }

    except ImportError as e:
        logger.error(f"Firebase dependencies not available: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to save to Firebase: {e}", exc_info=True)
        raise


async def promote_fields(
    doc_id: str,
    filename: str,
    document_type: str,
    fields: List[Dict[str, Any]],
    destination: str,
    source_text: Optional[str] = None,
    additional_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Promote extracted fields to specified destination(s)

    Args:
        doc_id: Document UUID
        filename: Original filename
        document_type: Type of document (stop_loss, spd, 834, etc.)
        fields: List of extracted field dictionaries
        destination: Comma-separated destinations: "neon", "firebase", "n8n"
        source_text: Optional original OCR text
        additional_metadata: Optional additional metadata

    Returns:
        Dictionary with promotion results for each destination

    Example:
        result = await promote_fields(
            doc_id="uuid",
            filename="doc.pdf",
            document_type="stop_loss",
            fields=[...],
            destination="neon,n8n"
        )
    """

    # Prepare metadata
    metadata = {
        "doc_id": doc_id,
        "filename": filename,
        "document_type": document_type,
        "source_text": source_text or "",
        "promoted_at": datetime.utcnow().isoformat()
    }

    # Add additional metadata if provided
    if additional_metadata:
        metadata.update(additional_metadata)

    # Parse destinations
    destinations = [d.strip().lower() for d in destination.split(',')]

    logger.info(f"Promoting fields to destinations: {destinations}")

    results = {
        "doc_id": doc_id,
        "filename": filename,
        "document_type": document_type,
        "field_count": len(fields),
        "destinations": destinations,
        "results": []
    }

    # Process each destination
    for dest in destinations:
        try:
            if dest == "neon":
                result = await save_to_neon(fields, metadata)
                results["results"].append(result)

            elif dest == "firebase":
                result = await save_to_firebase(fields, metadata)
                results["results"].append(result)

            elif dest == "n8n":
                result = await trigger_n8n_webhook(doc_id, fields, metadata)
                results["results"].append(result)

            else:
                logger.warning(f"Unknown destination: {dest}")
                results["results"].append({
                    "success": False,
                    "destination": dest,
                    "message": f"Unknown destination: {dest}"
                })

        except Exception as e:
            logger.error(f"Failed to promote to {dest}: {e}")
            results["results"].append({
                "success": False,
                "destination": dest,
                "error": str(e),
                "message": f"Failed to promote to {dest}"
            })

    # Overall success if at least one destination succeeded
    results["overall_success"] = any(r.get("success", False) for r in results["results"])

    return results


async def create_neon_table() -> Dict[str, Any]:
    """
    Create the doc_parser_fillable table in Neon if it doesn't exist

    Returns:
        Dictionary with creation status
    """

    if not NEON_URL:
        raise ValueError("NEON_URL not configured")

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS doc_parser_fillable (
        id SERIAL PRIMARY KEY,
        doc_id UUID NOT NULL,
        filename TEXT,
        field_name TEXT,
        field_value TEXT,
        matched_field TEXT,
        confidence NUMERIC(3,2),
        source_text TEXT,
        document_type TEXT,
        parsed_at TIMESTAMPTZ DEFAULT NOW()
    );

    -- Create indexes for common queries
    CREATE INDEX IF NOT EXISTS idx_doc_parser_doc_id ON doc_parser_fillable(doc_id);
    CREATE INDEX IF NOT EXISTS idx_doc_parser_filename ON doc_parser_fillable(filename);
    CREATE INDEX IF NOT EXISTS idx_doc_parser_document_type ON doc_parser_fillable(document_type);
    CREATE INDEX IF NOT EXISTS idx_doc_parser_parsed_at ON doc_parser_fillable(parsed_at DESC);
    """

    try:
        conn = await asyncpg.connect(NEON_URL)

        try:
            await conn.execute(create_table_sql)
            logger.info("Successfully created/verified doc_parser_fillable table")

            return {
                "success": True,
                "message": "Table doc_parser_fillable created/verified successfully"
            }

        finally:
            await conn.close()

    except Exception as e:
        logger.error(f"Failed to create table: {e}", exc_info=True)
        raise


# Utility functions

def validate_fields(fields: List[Dict[str, Any]]) -> bool:
    """
    Validate that fields have required structure

    Args:
        fields: List of field dictionaries

    Returns:
        True if valid, raises ValueError if invalid
    """
    required_keys = ['label', 'value', 'matched_field', 'confidence']

    for i, field in enumerate(fields):
        if not isinstance(field, dict):
            raise ValueError(f"Field {i} is not a dictionary")

        for key in required_keys:
            if key not in field:
                raise ValueError(f"Field {i} missing required key: {key}")

    return True


def get_promotion_summary(results: Dict[str, Any]) -> str:
    """
    Generate a human-readable summary of promotion results

    Args:
        results: Results dictionary from promote_fields()

    Returns:
        Formatted summary string
    """
    summary_lines = [
        f"Document: {results.get('filename', 'unknown')}",
        f"Doc ID: {results.get('doc_id', 'unknown')}",
        f"Type: {results.get('document_type', 'unknown')}",
        f"Fields: {results.get('field_count', 0)}",
        f"Destinations: {', '.join(results.get('destinations', []))}",
        "",
        "Results:"
    ]

    for result in results.get('results', []):
        dest = result.get('destination', 'unknown')
        success = "✓" if result.get('success', False) else "✗"
        message = result.get('message', 'No message')
        summary_lines.append(f"  {success} {dest}: {message}")

    return "\n".join(summary_lines)
