"""
Field Extractor Module
Extracts structured fields from unstructured OCR text
"""

import re
import json
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class FieldExtractor:
    """Extract structured fields from unstructured text"""

    def __init__(self, mapping_file: Optional[str] = None):
        """
        Initialize field extractor

        Args:
            mapping_file: Path to field_mapping.json (optional)
        """
        self.field_mappings = {}
        if mapping_file and Path(mapping_file).exists():
            with open(mapping_file, 'r') as f:
                self.field_mappings = json.load(f)
            logger.info(f"Loaded field mappings from {mapping_file}")
        else:
            # Default field mappings if no file provided
            self.field_mappings = self._get_default_mappings()

    def _get_default_mappings(self) -> Dict[str, str]:
        """
        Get default field name mappings

        Returns:
            Dictionary mapping display labels to schema field names
        """
        return {
            # Stop-Loss fields
            "stop-loss deductible": "stop_loss_deductible",
            "stop loss deductible": "stop_loss_deductible",
            "aggregate deductible": "aggregate_deductible",
            "specific deductible": "specific_deductible",
            "individual deductible": "specific_deductible",
            "corridor": "corridor",
            "corridor deductible": "corridor",

            # Contract fields
            "contract type": "contract_type",
            "contract number": "contract_number",
            "policy number": "policy_number",
            "group number": "group_number",
            "effective date": "effective_date",
            "renewal date": "renewal_date",
            "termination date": "termination_date",
            "expiration date": "expiration_date",

            # Member/Coverage fields
            "total members": "total_members",
            "enrolled members": "enrolled_members",
            "eligible members": "eligible_members",
            "lives covered": "lives_covered",
            "employee count": "employee_count",

            # Premium fields
            "premium": "premium",
            "monthly premium": "monthly_premium",
            "annual premium": "annual_premium",
            "rate": "rate",
            "per member per month": "pmpm",
            "pmpm": "pmpm",

            # Plan fields
            "plan name": "plan_name",
            "plan type": "plan_type",
            "network": "network",
            "carrier": "carrier",
            "broker": "broker",
            "tpa": "tpa",
            "third party administrator": "tpa",

            # Coverage amounts
            "max benefit": "max_benefit",
            "maximum benefit": "max_benefit",
            "lifetime maximum": "lifetime_maximum",
            "out of pocket max": "out_of_pocket_max",
            "out-of-pocket maximum": "out_of_pocket_max",
            "oop max": "out_of_pocket_max",

            # Employer info
            "employer name": "employer_name",
            "company name": "company_name",
            "organization": "organization",
            "sic code": "sic_code",
            "industry": "industry",

            # Contact info
            "address": "address",
            "city": "city",
            "state": "state",
            "zip": "zip_code",
            "zip code": "zip_code",
            "phone": "phone",
            "email": "email",
            "contact": "contact_name",
        }

    def extract_fields_from_text(self, raw_text: str) -> List[Dict[str, Any]]:
        """
        Extract structured fields from raw OCR text

        Args:
            raw_text: Unstructured text from OCR or document

        Returns:
            List of structured field dictionaries with label, value, matched_field, and confidence
        """
        if not raw_text or not raw_text.strip():
            logger.warning("Empty text provided for field extraction")
            return []

        extracted_fields = []

        # Pattern 1: Key-Value pairs with colon separator (most common)
        # Example: "Stop-Loss Deductible: $25,000"
        colon_pattern = r'([A-Za-z][\w\s\-/()]+?)\s*:\s*([^\n\r]+)'
        colon_matches = re.finditer(colon_pattern, raw_text, re.MULTILINE)

        for match in colon_matches:
            label = match.group(1).strip()
            value = match.group(2).strip()

            # Skip if value is too long (likely not a single field value)
            if len(value) > 200:
                continue

            # Skip common false positives
            if self._is_false_positive(label, value):
                continue

            field_data = self._create_field_entry(label, value)
            extracted_fields.append(field_data)

        # Pattern 2: Key-Value with equals or dash
        # Example: "Plan Name = Blue Shield PPO" or "Plan Name - Blue Shield PPO"
        equals_pattern = r'([A-Za-z][\w\s\-/()]+?)\s*[=\-]\s*([^\n\r]+)'
        equals_matches = re.finditer(equals_pattern, raw_text, re.MULTILINE)

        for match in equals_matches:
            label = match.group(1).strip()
            value = match.group(2).strip()

            if len(value) > 200 or self._is_false_positive(label, value):
                continue

            # Check if we already have this field from colon pattern
            if not any(f['label'] == label for f in extracted_fields):
                field_data = self._create_field_entry(label, value)
                extracted_fields.append(field_data)

        # Pattern 3: Dollar amounts with labels
        # Example: "Stop-Loss Deductible $25,000"
        dollar_pattern = r'([A-Za-z][\w\s\-/()]+?)\s+(\$[\d,]+(?:\.\d{2})?)'
        dollar_matches = re.finditer(dollar_pattern, raw_text)

        for match in dollar_matches:
            label = match.group(1).strip()
            value = match.group(2).strip()

            if not any(f['label'] == label for f in extracted_fields):
                field_data = self._create_field_entry(label, value)
                extracted_fields.append(field_data)

        # Pattern 4: Labeled tables or structured data
        # Example: "Field Name    Value"
        table_fields = self._extract_table_fields(raw_text)
        for field_data in table_fields:
            if not any(f['label'] == field_data['label'] for f in extracted_fields):
                extracted_fields.append(field_data)

        # Pattern 5: Dates with labels
        date_fields = self._extract_date_fields(raw_text)
        for field_data in date_fields:
            if not any(f['label'] == field_data['label'] for f in extracted_fields):
                extracted_fields.append(field_data)

        # Sort by confidence (highest first)
        extracted_fields.sort(key=lambda x: x['confidence'], reverse=True)

        logger.info(f"Extracted {len(extracted_fields)} fields from text")
        return extracted_fields

    def _create_field_entry(self, label: str, value: str) -> Dict[str, Any]:
        """
        Create a structured field entry

        Args:
            label: Field label/name
            value: Field value

        Returns:
            Dictionary with label, value, matched_field, and confidence
        """
        # Normalize label for matching
        normalized_label = label.lower().strip()

        # Find matching schema field
        matched_field = self.field_mappings.get(normalized_label)

        # Calculate confidence based on match quality
        confidence = self._calculate_confidence(label, value, matched_field)

        return {
            "label": label,
            "value": value,
            "matched_field": matched_field if matched_field else self._normalize_field_name(label),
            "confidence": confidence
        }

    def _normalize_field_name(self, label: str) -> str:
        """
        Convert label to snake_case field name

        Args:
            label: Original field label

        Returns:
            Normalized snake_case field name
        """
        # Remove special characters except spaces and hyphens
        cleaned = re.sub(r'[^\w\s\-]', '', label)

        # Replace spaces and hyphens with underscores
        normalized = re.sub(r'[\s\-]+', '_', cleaned)

        # Convert to lowercase
        normalized = normalized.lower().strip('_')

        return normalized

    def _calculate_confidence(self, label: str, value: str, matched_field: Optional[str]) -> float:
        """
        Calculate confidence score for extracted field

        Args:
            label: Field label
            value: Field value
            matched_field: Matched schema field (if any)

        Returns:
            Confidence score between 0.0 and 1.0
        """
        confidence = 0.5  # Base confidence

        # Boost confidence if we have a schema match
        if matched_field and matched_field in self.field_mappings.values():
            confidence += 0.3

        # Boost confidence for well-formatted values
        if re.match(r'^\$[\d,]+(?:\.\d{2})?$', value):  # Dollar amount
            confidence += 0.1
        elif re.match(r'^\d{1,2}[/-]\d{1,2}[/-]\d{2,4}$', value):  # Date
            confidence += 0.1
        elif re.match(r'^[\d,]+$', value):  # Number
            confidence += 0.05
        elif re.match(r'^[A-Z0-9\-]+$', value):  # Code/ID
            confidence += 0.05

        # Reduce confidence for very short or very long values
        if len(value) < 2:
            confidence -= 0.2
        elif len(value) > 100:
            confidence -= 0.1

        # Ensure confidence is between 0 and 1
        return max(0.0, min(1.0, confidence))

    def _is_false_positive(self, label: str, value: str) -> bool:
        """
        Check if a field is likely a false positive

        Args:
            label: Field label
            value: Field value

        Returns:
            True if likely false positive
        """
        # Skip empty values
        if not value or not value.strip():
            return True

        # Skip single characters
        if len(value) == 1:
            return True

        # Skip common document headers/footers
        false_positive_patterns = [
            r'^page\s+\d+',
            r'^\d+\s+of\s+\d+$',
            r'^confidential',
            r'^proprietary',
            r'^copyright',
            r'^all rights reserved',
        ]

        value_lower = value.lower()
        for pattern in false_positive_patterns:
            if re.match(pattern, value_lower):
                return True

        return False

    def _extract_table_fields(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract fields from table-like structures

        Args:
            text: Raw text

        Returns:
            List of extracted fields
        """
        fields = []

        # Look for lines with multiple spaces/tabs (table-like structure)
        lines = text.split('\n')
        for line in lines:
            # Check if line has multiple segments separated by 2+ spaces or tabs
            parts = re.split(r'\s{2,}|\t+', line.strip())

            if len(parts) == 2:
                label, value = parts
                # Validate that both parts look like label and value
                if len(label) > 2 and len(value) > 0 and len(value) < 100:
                    field_data = self._create_field_entry(label, value)
                    fields.append(field_data)

        return fields

    def _extract_date_fields(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract date fields with common date labels

        Args:
            text: Raw text

        Returns:
            List of extracted date fields
        """
        fields = []

        # Common date field labels
        date_labels = [
            'effective date', 'renewal date', 'termination date',
            'expiration date', 'start date', 'end date',
            'issue date', 'anniversary date'
        ]

        # Date patterns
        date_patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # MM/DD/YYYY or MM-DD-YYYY
            r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',    # YYYY-MM-DD
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}',  # Month DD, YYYY
        ]

        for label in date_labels:
            # Look for the label followed by a date
            for date_pattern in date_patterns:
                pattern = rf'{label}\s*[:\-=]?\s*({date_pattern})'
                matches = re.finditer(pattern, text, re.IGNORECASE)

                for match in matches:
                    date_value = match.group(1).strip()
                    field_data = self._create_field_entry(label.title(), date_value)
                    fields.append(field_data)

        return fields

    def extract_fields_with_context(
        self,
        raw_text: str,
        document_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract fields with additional context information

        Args:
            raw_text: Unstructured text
            document_type: Optional document type hint (e.g., 'stop_loss', 'spd', '834')

        Returns:
            Dictionary with fields and metadata
        """
        fields = self.extract_fields_from_text(raw_text)

        # Group fields by category
        categorized_fields = self._categorize_fields(fields)

        # Calculate overall extraction quality
        quality_score = self._calculate_extraction_quality(fields)

        return {
            "fields": fields,
            "categorized_fields": categorized_fields,
            "document_type": document_type,
            "total_fields": len(fields),
            "high_confidence_count": len([f for f in fields if f['confidence'] >= 0.8]),
            "quality_score": quality_score,
            "metadata": {
                "text_length": len(raw_text),
                "line_count": raw_text.count('\n'),
            }
        }

    def _categorize_fields(self, fields: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Categorize fields into logical groups

        Args:
            fields: List of extracted fields

        Returns:
            Dictionary with categorized fields
        """
        categories = {
            "financial": [],
            "coverage": [],
            "dates": [],
            "identifiers": [],
            "contact": [],
            "other": []
        }

        financial_keywords = ['premium', 'deductible', 'cost', 'rate', 'amount', 'price', 'dollar']
        coverage_keywords = ['plan', 'benefit', 'coverage', 'network', 'max', 'limit']
        date_keywords = ['date', 'effective', 'renewal', 'expiration', 'termination']
        id_keywords = ['number', 'id', 'code', 'contract', 'policy', 'group']
        contact_keywords = ['address', 'phone', 'email', 'contact', 'city', 'state', 'zip']

        for field in fields:
            label_lower = field['label'].lower()
            value_lower = field['value'].lower()

            categorized = False

            # Check financial
            if any(kw in label_lower for kw in financial_keywords) or '$' in field['value']:
                categories['financial'].append(field)
                categorized = True

            # Check coverage
            elif any(kw in label_lower for kw in coverage_keywords):
                categories['coverage'].append(field)
                categorized = True

            # Check dates
            elif any(kw in label_lower for kw in date_keywords):
                categories['dates'].append(field)
                categorized = True

            # Check identifiers
            elif any(kw in label_lower for kw in id_keywords):
                categories['identifiers'].append(field)
                categorized = True

            # Check contact
            elif any(kw in label_lower for kw in contact_keywords):
                categories['contact'].append(field)
                categorized = True

            # Default to other
            if not categorized:
                categories['other'].append(field)

        return categories

    def _calculate_extraction_quality(self, fields: List[Dict[str, Any]]) -> float:
        """
        Calculate overall extraction quality score

        Args:
            fields: List of extracted fields

        Returns:
            Quality score between 0.0 and 1.0
        """
        if not fields:
            return 0.0

        # Average confidence of all fields
        avg_confidence = sum(f['confidence'] for f in fields) / len(fields)

        # Bonus for having many fields
        field_count_bonus = min(0.2, len(fields) / 100)

        # Bonus for having matched fields
        matched_count = sum(1 for f in fields if f['matched_field'] in self.field_mappings.values())
        matched_bonus = min(0.2, matched_count / len(fields))

        quality = avg_confidence + field_count_bonus + matched_bonus

        return min(1.0, quality)


# Convenience function for direct use
def extract_fields_from_text(
    raw_text: str,
    mapping_file: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Extract structured fields from raw text

    Args:
        raw_text: Unstructured OCR text
        mapping_file: Optional path to field_mapping.json

    Returns:
        List of structured field dictionaries
    """
    extractor = FieldExtractor(mapping_file=mapping_file)
    return extractor.extract_fields_from_text(raw_text)
