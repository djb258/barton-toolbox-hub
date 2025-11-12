"""
Unit tests for validation schemas.
Tests schema loading, validation, and integration.
"""
import pytest
import json
import tempfile
import os
from backend.tools.validator.core.validator import (
    FieldValidator,
    ValidationSchema,
    ValidationRule,
    ValidationType,
    Severity
)


class TestValidationSchema:
    """Test ValidationSchema class"""

    def test_schema_creation(self):
        """Test creating a validation schema"""
        schema = ValidationSchema(
            schema_id="test_schema",
            name="Test Schema",
            description="A test schema"
        )
        assert schema.schema_id == "test_schema"
        assert schema.name == "Test Schema"
        assert schema.description == "A test schema"
        assert len(schema.rules) == 0

    def test_schema_add_rule(self):
        """Test adding rules to schema"""
        schema = ValidationSchema(
            schema_id="test_schema",
            name="Test Schema"
        )

        rule = ValidationRule(
            field="test_field",
            rule_type=ValidationType.REQUIRED
        )

        schema.add_rule(rule)
        assert len(schema.rules) == 1
        assert schema.rules[0].field == "test_field"

    def test_schema_validate_success(self):
        """Test schema validation passes with valid data"""
        schema = ValidationSchema(
            schema_id="test_schema",
            name="Test Schema"
        )

        schema.add_rule(ValidationRule(
            field="name",
            rule_type=ValidationType.REQUIRED
        ))
        schema.add_rule(ValidationRule(
            field="age",
            rule_type=ValidationType.TYPE,
            expected_type="number"
        ))

        result = schema.validate({
            "name": "John",
            "age": 30
        })

        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_schema_validate_failure(self):
        """Test schema validation fails with invalid data"""
        schema = ValidationSchema(
            schema_id="test_schema",
            name="Test Schema"
        )

        schema.add_rule(ValidationRule(
            field="name",
            rule_type=ValidationType.REQUIRED
        ))
        schema.add_rule(ValidationRule(
            field="age",
            rule_type=ValidationType.TYPE,
            expected_type="number"
        ))

        result = schema.validate({
            "name": "",  # Empty (required field)
            "age": "not a number"  # Wrong type
        })

        assert result["valid"] is False
        assert len(result["errors"]) == 2

    def test_schema_validate_with_warnings(self):
        """Test schema validation with warnings"""
        schema = ValidationSchema(
            schema_id="test_schema",
            name="Test Schema"
        )

        schema.add_rule(ValidationRule(
            field="name",
            rule_type=ValidationType.REQUIRED,
            severity=Severity.ERROR
        ))
        schema.add_rule(ValidationRule(
            field="email",
            rule_type=ValidationType.REQUIRED,
            severity=Severity.WARNING
        ))

        result = schema.validate({
            "name": "John",
            # email missing
        })

        assert result["valid"] is True  # No errors
        assert len(result["errors"]) == 0
        assert len(result["warnings"]) == 1
        assert result["warnings"][0]["field"] == "email"

    def test_schema_to_dict(self):
        """Test converting schema to dictionary"""
        schema = ValidationSchema(
            schema_id="test_schema",
            name="Test Schema",
            description="Test description"
        )

        schema.add_rule(ValidationRule(
            field="name",
            rule_type=ValidationType.REQUIRED
        ))

        schema_dict = schema.to_dict()

        assert schema_dict["schema_id"] == "test_schema"
        assert schema_dict["name"] == "Test Schema"
        assert schema_dict["rule_count"] == 1
        assert len(schema_dict["rules"]) == 1


class TestFieldValidator:
    """Test FieldValidator class"""

    def test_validator_creation(self):
        """Test creating a field validator"""
        with tempfile.TemporaryDirectory() as tmpdir:
            validator = FieldValidator(schemas_dir=tmpdir)
            assert len(validator.schemas) == 0

    def test_validator_load_schemas(self):
        """Test loading schemas from directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test schema file
            schema_data = {
                "schema_id": "test_schema",
                "name": "Test Schema",
                "description": "Test",
                "rules": [
                    {
                        "field": "name",
                        "rule_type": "required",
                        "severity": "error",
                        "params": {}
                    }
                ]
            }

            schema_file = os.path.join(tmpdir, "test_schema.json")
            with open(schema_file, "w") as f:
                json.dump(schema_data, f)

            # Load schemas
            validator = FieldValidator(schemas_dir=tmpdir)
            assert len(validator.schemas) == 1
            assert "test_schema" in validator.schemas

    def test_validator_validate_with_schema_id(self):
        """Test validation with specific schema ID"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create schema
            schema_data = {
                "schema_id": "test_schema",
                "name": "Test Schema",
                "description": "Test",
                "rules": [
                    {
                        "field": "name",
                        "rule_type": "required",
                        "severity": "error",
                        "params": {}
                    },
                    {
                        "field": "age",
                        "rule_type": "type",
                        "severity": "error",
                        "params": {
                            "expected_type": "number"
                        }
                    }
                ]
            }

            schema_file = os.path.join(tmpdir, "test_schema.json")
            with open(schema_file, "w") as f:
                json.dump(schema_data, f)

            validator = FieldValidator(schemas_dir=tmpdir)

            # Validate valid data
            result = validator.validate(
                fields={"name": "John", "age": 30},
                schema_id="test_schema"
            )

            assert result["valid"] is True
            assert result["schema_id"] == "test_schema"

            # Validate invalid data
            result = validator.validate(
                fields={"name": "", "age": "not a number"},
                schema_id="test_schema"
            )

            assert result["valid"] is False
            assert len(result["errors"]) > 0

    def test_validator_validate_all_schemas(self):
        """Test validation against all schemas"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multiple schemas
            schema1 = {
                "schema_id": "schema1",
                "name": "Schema 1",
                "rules": [
                    {
                        "field": "name",
                        "rule_type": "required",
                        "severity": "error",
                        "params": {}
                    }
                ]
            }

            schema2 = {
                "schema_id": "schema2",
                "name": "Schema 2",
                "rules": [
                    {
                        "field": "email",
                        "rule_type": "required",
                        "severity": "error",
                        "params": {}
                    }
                ]
            }

            with open(os.path.join(tmpdir, "schema1.json"), "w") as f:
                json.dump(schema1, f)
            with open(os.path.join(tmpdir, "schema2.json"), "w") as f:
                json.dump(schema2, f)

            validator = FieldValidator(schemas_dir=tmpdir)

            # Validate - should fail both schemas
            result = validator.validate(fields={})

            assert result["valid"] is False
            assert len(result["errors"]) == 2  # Both name and email missing
            assert len(result["schemas_checked"]) == 2

    def test_validator_schema_not_found(self):
        """Test validation with non-existent schema"""
        with tempfile.TemporaryDirectory() as tmpdir:
            validator = FieldValidator(schemas_dir=tmpdir)

            result = validator.validate(
                fields={"name": "John"},
                schema_id="non_existent"
            )

            assert result["valid"] is False
            assert "not found" in result["errors"][0]["message"]

    def test_validator_get_schema(self):
        """Test getting a schema by ID"""
        with tempfile.TemporaryDirectory() as tmpdir:
            schema_data = {
                "schema_id": "test_schema",
                "name": "Test Schema",
                "rules": []
            }

            with open(os.path.join(tmpdir, "test.json"), "w") as f:
                json.dump(schema_data, f)

            validator = FieldValidator(schemas_dir=tmpdir)

            schema = validator.get_schema("test_schema")
            assert schema is not None
            assert schema.schema_id == "test_schema"

            schema = validator.get_schema("non_existent")
            assert schema is None

    def test_validator_list_schemas(self):
        """Test listing all schemas"""
        with tempfile.TemporaryDirectory() as tmpdir:
            schema_data = {
                "schema_id": "test_schema",
                "name": "Test Schema",
                "description": "Test description",
                "rules": [
                    {
                        "field": "name",
                        "rule_type": "required",
                        "severity": "error",
                        "params": {}
                    }
                ]
            }

            with open(os.path.join(tmpdir, "test.json"), "w") as f:
                json.dump(schema_data, f)

            validator = FieldValidator(schemas_dir=tmpdir)

            schemas = validator.list_schemas()
            assert len(schemas) == 1
            assert schemas[0]["schema_id"] == "test_schema"
            assert schemas[0]["name"] == "Test Schema"
            assert schemas[0]["rule_count"] == 1

    def test_validator_add_schema_programmatically(self):
        """Test adding a schema programmatically"""
        with tempfile.TemporaryDirectory() as tmpdir:
            validator = FieldValidator(schemas_dir=tmpdir)

            # Create schema
            schema = ValidationSchema(
                schema_id="dynamic_schema",
                name="Dynamic Schema"
            )
            schema.add_rule(ValidationRule(
                field="test",
                rule_type=ValidationType.REQUIRED
            ))

            # Add to validator
            validator.add_schema(schema)

            assert "dynamic_schema" in validator.schemas
            assert len(validator.schemas) == 1


class TestRealWorldScenarios:
    """Test real-world validation scenarios"""

    def test_document_validation_complete(self):
        """Test complete document validation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create document validation schema
            schema_data = {
                "schema_id": "document_complete",
                "name": "Complete Document Validation",
                "rules": [
                    {
                        "field": "policy_number",
                        "rule_type": "required",
                        "severity": "error",
                        "params": {}
                    },
                    {
                        "field": "policy_number",
                        "rule_type": "regex",
                        "severity": "error",
                        "params": {
                            "pattern": "^[A-Z0-9-]+$"
                        }
                    },
                    {
                        "field": "stop_loss_deductible",
                        "rule_type": "type",
                        "severity": "error",
                        "params": {
                            "expected_type": "number"
                        }
                    },
                    {
                        "field": "stop_loss_deductible",
                        "rule_type": "range",
                        "severity": "error",
                        "params": {
                            "min": 0,
                            "max": 10000000
                        }
                    },
                    {
                        "field": "effective_date",
                        "rule_type": "date_format",
                        "severity": "error",
                        "params": {
                            "format": "%Y-%m-%d"
                        }
                    }
                ]
            }

            with open(os.path.join(tmpdir, "document.json"), "w") as f:
                json.dump(schema_data, f)

            validator = FieldValidator(schemas_dir=tmpdir)

            # Test valid document
            valid_doc = {
                "policy_number": "ABC-123",
                "stop_loss_deductible": 50000,
                "effective_date": "2024-01-01"
            }

            result = validator.validate(
                fields=valid_doc,
                schema_id="document_complete"
            )

            assert result["valid"] is True
            assert len(result["errors"]) == 0

            # Test invalid document
            invalid_doc = {
                "policy_number": "abc-123",  # lowercase not allowed
                "stop_loss_deductible": -1000,  # negative not allowed
                "effective_date": "01/01/2024"  # wrong format
            }

            result = validator.validate(
                fields=invalid_doc,
                schema_id="document_complete"
            )

            assert result["valid"] is False
            assert len(result["errors"]) >= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
