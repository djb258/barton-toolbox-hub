"""
Field Validator Engine
Validates document fields against defined schemas and rules.
"""
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime
import re
import json
import os
from enum import Enum


class ValidationType(str, Enum):
    """Validation rule types"""
    REQUIRED = "required"
    TYPE = "type"
    RANGE = "range"
    REGEX = "regex"
    LENGTH = "length"
    ENUM = "enum"
    DATE_FORMAT = "date_format"
    CUSTOM = "custom"


class Severity(str, Enum):
    """Validation error severity levels"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationError:
    """Represents a validation error"""

    def __init__(
        self,
        field: str,
        rule_type: ValidationType,
        message: str,
        severity: Severity = Severity.ERROR,
        expected: Any = None,
        actual: Any = None,
        rule_id: Optional[str] = None
    ):
        self.field = field
        self.rule_type = rule_type
        self.message = message
        self.severity = severity
        self.expected = expected
        self.actual = actual
        self.rule_id = rule_id
        self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "field": self.field,
            "rule_type": self.rule_type.value,
            "message": self.message,
            "severity": self.severity.value,
            "expected": self.expected,
            "actual": self.actual,
            "rule_id": self.rule_id,
            "timestamp": self.timestamp
        }


class ValidationRule:
    """Represents a single validation rule"""

    def __init__(
        self,
        field: str,
        rule_type: ValidationType,
        rule_id: Optional[str] = None,
        severity: Severity = Severity.ERROR,
        **kwargs
    ):
        self.field = field
        self.rule_type = rule_type
        self.rule_id = rule_id or f"{field}_{rule_type.value}"
        self.severity = severity
        self.params = kwargs

    def validate(self, value: Any) -> Optional[ValidationError]:
        """
        Validate a value against this rule.
        Returns ValidationError if validation fails, None if passes.
        """
        # REQUIRED check
        if self.rule_type == ValidationType.REQUIRED:
            if value is None or value == "" or value == []:
                return ValidationError(
                    field=self.field,
                    rule_type=self.rule_type,
                    message=f"Field '{self.field}' is required",
                    severity=self.severity,
                    expected="non-empty value",
                    actual=value,
                    rule_id=self.rule_id
                )

        # Skip further checks if value is None/empty and not required
        if value is None or value == "":
            return None

        # TYPE check
        if self.rule_type == ValidationType.TYPE:
            expected_type = self.params.get("expected_type")
            if expected_type:
                if not self._check_type(value, expected_type):
                    return ValidationError(
                        field=self.field,
                        rule_type=self.rule_type,
                        message=f"Field '{self.field}' must be of type {expected_type}",
                        severity=self.severity,
                        expected=expected_type,
                        actual=type(value).__name__,
                        rule_id=self.rule_id
                    )

        # RANGE check (for numbers)
        if self.rule_type == ValidationType.RANGE:
            min_val = self.params.get("min")
            max_val = self.params.get("max")
            try:
                num_value = float(value)
                if min_val is not None and num_value < min_val:
                    return ValidationError(
                        field=self.field,
                        rule_type=self.rule_type,
                        message=f"Field '{self.field}' must be >= {min_val}",
                        severity=self.severity,
                        expected=f">= {min_val}",
                        actual=num_value,
                        rule_id=self.rule_id
                    )
                if max_val is not None and num_value > max_val:
                    return ValidationError(
                        field=self.field,
                        rule_type=self.rule_type,
                        message=f"Field '{self.field}' must be <= {max_val}",
                        severity=self.severity,
                        expected=f"<= {max_val}",
                        actual=num_value,
                        rule_id=self.rule_id
                    )
            except (ValueError, TypeError):
                return ValidationError(
                    field=self.field,
                    rule_type=self.rule_type,
                    message=f"Field '{self.field}' must be a valid number for range check",
                    severity=self.severity,
                    expected="numeric value",
                    actual=str(value),
                    rule_id=self.rule_id
                )

        # REGEX check
        if self.rule_type == ValidationType.REGEX:
            pattern = self.params.get("pattern")
            if pattern:
                if not re.match(pattern, str(value)):
                    return ValidationError(
                        field=self.field,
                        rule_type=self.rule_type,
                        message=f"Field '{self.field}' does not match required pattern",
                        severity=self.severity,
                        expected=f"pattern: {pattern}",
                        actual=str(value),
                        rule_id=self.rule_id
                    )

        # LENGTH check (for strings, lists)
        if self.rule_type == ValidationType.LENGTH:
            min_len = self.params.get("min")
            max_len = self.params.get("max")
            length = len(value) if hasattr(value, "__len__") else None

            if length is not None:
                if min_len is not None and length < min_len:
                    return ValidationError(
                        field=self.field,
                        rule_type=self.rule_type,
                        message=f"Field '{self.field}' must have length >= {min_len}",
                        severity=self.severity,
                        expected=f"length >= {min_len}",
                        actual=f"length = {length}",
                        rule_id=self.rule_id
                    )
                if max_len is not None and length > max_len:
                    return ValidationError(
                        field=self.field,
                        rule_type=self.rule_type,
                        message=f"Field '{self.field}' must have length <= {max_len}",
                        severity=self.severity,
                        expected=f"length <= {max_len}",
                        actual=f"length = {length}",
                        rule_id=self.rule_id
                    )

        # ENUM check
        if self.rule_type == ValidationType.ENUM:
            allowed_values = self.params.get("allowed_values", [])
            if value not in allowed_values:
                return ValidationError(
                    field=self.field,
                    rule_type=self.rule_type,
                    message=f"Field '{self.field}' must be one of: {', '.join(map(str, allowed_values))}",
                    severity=self.severity,
                    expected=allowed_values,
                    actual=value,
                    rule_id=self.rule_id
                )

        # DATE_FORMAT check
        if self.rule_type == ValidationType.DATE_FORMAT:
            date_format = self.params.get("format", "%Y-%m-%d")
            try:
                datetime.strptime(str(value), date_format)
            except ValueError:
                return ValidationError(
                    field=self.field,
                    rule_type=self.rule_type,
                    message=f"Field '{self.field}' must be in format {date_format}",
                    severity=self.severity,
                    expected=date_format,
                    actual=str(value),
                    rule_id=self.rule_id
                )

        # CUSTOM check
        if self.rule_type == ValidationType.CUSTOM:
            validator_func = self.params.get("validator")
            if validator_func and callable(validator_func):
                result = validator_func(value)
                if result is not True:
                    error_msg = result if isinstance(result, str) else f"Custom validation failed for '{self.field}'"
                    return ValidationError(
                        field=self.field,
                        rule_type=self.rule_type,
                        message=error_msg,
                        severity=self.severity,
                        actual=value,
                        rule_id=self.rule_id
                    )

        return None

    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected type"""
        type_map = {
            "string": str,
            "str": str,
            "number": (int, float),
            "int": int,
            "integer": int,
            "float": float,
            "bool": bool,
            "boolean": bool,
            "list": list,
            "array": list,
            "dict": dict,
            "object": dict
        }

        expected = type_map.get(expected_type.lower())
        if expected:
            return isinstance(value, expected)
        return True


class ValidationSchema:
    """Represents a validation schema with multiple rules"""

    def __init__(self, schema_id: str, name: str, description: str = ""):
        self.schema_id = schema_id
        self.name = name
        self.description = description
        self.rules: List[ValidationRule] = []

    def add_rule(self, rule: ValidationRule):
        """Add a validation rule to this schema"""
        self.rules.append(rule)

    def validate(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate fields against all rules in this schema.

        Returns:
            {
                "valid": bool,
                "errors": List[dict],
                "warnings": List[dict],
                "info": List[dict],
                "fields_validated": int,
                "rules_checked": int
            }
        """
        errors = []
        warnings = []
        info = []

        for rule in self.rules:
            field_value = fields.get(rule.field)
            validation_error = rule.validate(field_value)

            if validation_error:
                error_dict = validation_error.to_dict()

                if validation_error.severity == Severity.ERROR:
                    errors.append(error_dict)
                elif validation_error.severity == Severity.WARNING:
                    warnings.append(error_dict)
                elif validation_error.severity == Severity.INFO:
                    info.append(error_dict)

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "info": info,
            "fields_validated": len(set(rule.field for rule in self.rules)),
            "rules_checked": len(self.rules)
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert schema to dictionary"""
        return {
            "schema_id": self.schema_id,
            "name": self.name,
            "description": self.description,
            "rule_count": len(self.rules),
            "rules": [
                {
                    "rule_id": rule.rule_id,
                    "field": rule.field,
                    "rule_type": rule.rule_type.value,
                    "severity": rule.severity.value,
                    "params": rule.params
                }
                for rule in self.rules
            ]
        }


class FieldValidator:
    """Main field validator class"""

    def __init__(self, schemas_dir: Optional[str] = None):
        self.schemas: Dict[str, ValidationSchema] = {}
        self.schemas_dir = schemas_dir or os.path.join(
            os.path.dirname(__file__), "..", "schemas"
        )

        # Load schemas from directory
        self._load_schemas()

    def _load_schemas(self):
        """Load validation schemas from JSON files"""
        if not os.path.exists(self.schemas_dir):
            return

        for filename in os.listdir(self.schemas_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.schemas_dir, filename)
                try:
                    with open(filepath, "r") as f:
                        schema_data = json.load(f)
                        schema = self._schema_from_dict(schema_data)
                        self.schemas[schema.schema_id] = schema
                except Exception as e:
                    print(f"Error loading schema {filename}: {e}")

    def _schema_from_dict(self, data: Dict[str, Any]) -> ValidationSchema:
        """Create ValidationSchema from dictionary"""
        schema = ValidationSchema(
            schema_id=data.get("schema_id", ""),
            name=data.get("name", ""),
            description=data.get("description", "")
        )

        for rule_data in data.get("rules", []):
            rule = ValidationRule(
                field=rule_data["field"],
                rule_type=ValidationType(rule_data["rule_type"]),
                rule_id=rule_data.get("rule_id"),
                severity=Severity(rule_data.get("severity", "error")),
                **rule_data.get("params", {})
            )
            schema.add_rule(rule)

        return schema

    def validate(
        self,
        fields: Dict[str, Any],
        schema_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate fields against a schema.

        Args:
            fields: Dictionary of field name -> value pairs
            schema_id: Optional schema ID to use. If None, validates against all schemas.

        Returns:
            Validation results dictionary
        """
        if schema_id:
            if schema_id not in self.schemas:
                return {
                    "valid": False,
                    "errors": [{
                        "field": "_schema",
                        "message": f"Schema '{schema_id}' not found",
                        "severity": "error"
                    }],
                    "warnings": [],
                    "info": []
                }

            schema = self.schemas[schema_id]
            result = schema.validate(fields)
            result["schema_id"] = schema_id
            result["schema_name"] = schema.name
            return result
        else:
            # Validate against all schemas and combine results
            all_errors = []
            all_warnings = []
            all_info = []
            schemas_checked = []

            for schema_id, schema in self.schemas.items():
                result = schema.validate(fields)
                all_errors.extend(result["errors"])
                all_warnings.extend(result["warnings"])
                all_info.extend(result["info"])
                schemas_checked.append(schema_id)

            return {
                "valid": len(all_errors) == 0,
                "errors": all_errors,
                "warnings": all_warnings,
                "info": all_info,
                "schemas_checked": schemas_checked
            }

    def get_schema(self, schema_id: str) -> Optional[ValidationSchema]:
        """Get a schema by ID"""
        return self.schemas.get(schema_id)

    def list_schemas(self) -> List[Dict[str, Any]]:
        """List all available schemas"""
        return [
            {
                "schema_id": schema.schema_id,
                "name": schema.name,
                "description": schema.description,
                "rule_count": len(schema.rules)
            }
            for schema in self.schemas.values()
        ]

    def add_schema(self, schema: ValidationSchema):
        """Add a schema to the validator"""
        self.schemas[schema.schema_id] = schema
