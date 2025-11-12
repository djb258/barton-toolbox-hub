"""
Unit tests for validation rules.
Tests each validation rule type independently.
"""
import pytest
from datetime import datetime
from backend.tools.validator.core.validator import (
    ValidationRule,
    ValidationType,
    Severity,
    ValidationError
)


class TestRequiredRule:
    """Test REQUIRED validation rule"""

    def test_required_passes_with_value(self):
        """Test that required rule passes when value is present"""
        rule = ValidationRule(
            field="test_field",
            rule_type=ValidationType.REQUIRED
        )
        result = rule.validate("some value")
        assert result is None

    def test_required_fails_with_none(self):
        """Test that required rule fails when value is None"""
        rule = ValidationRule(
            field="test_field",
            rule_type=ValidationType.REQUIRED
        )
        result = rule.validate(None)
        assert isinstance(result, ValidationError)
        assert result.field == "test_field"
        assert result.rule_type == ValidationType.REQUIRED

    def test_required_fails_with_empty_string(self):
        """Test that required rule fails when value is empty string"""
        rule = ValidationRule(
            field="test_field",
            rule_type=ValidationType.REQUIRED
        )
        result = rule.validate("")
        assert isinstance(result, ValidationError)

    def test_required_fails_with_empty_list(self):
        """Test that required rule fails when value is empty list"""
        rule = ValidationRule(
            field="test_field",
            rule_type=ValidationType.REQUIRED
        )
        result = rule.validate([])
        assert isinstance(result, ValidationError)


class TestTypeRule:
    """Test TYPE validation rule"""

    def test_type_string_passes(self):
        """Test type check passes for valid string"""
        rule = ValidationRule(
            field="test_field",
            rule_type=ValidationType.TYPE,
            expected_type="string"
        )
        result = rule.validate("hello")
        assert result is None

    def test_type_string_fails(self):
        """Test type check fails for invalid string"""
        rule = ValidationRule(
            field="test_field",
            rule_type=ValidationType.TYPE,
            expected_type="string"
        )
        result = rule.validate(123)
        assert isinstance(result, ValidationError)
        assert result.expected == "string"
        assert result.actual == "int"

    def test_type_number_passes(self):
        """Test type check passes for valid number"""
        rule = ValidationRule(
            field="test_field",
            rule_type=ValidationType.TYPE,
            expected_type="number"
        )
        assert rule.validate(123) is None
        assert rule.validate(123.45) is None

    def test_type_number_fails(self):
        """Test type check fails for invalid number"""
        rule = ValidationRule(
            field="test_field",
            rule_type=ValidationType.TYPE,
            expected_type="number"
        )
        result = rule.validate("not a number")
        assert isinstance(result, ValidationError)

    def test_type_bool_passes(self):
        """Test type check passes for valid boolean"""
        rule = ValidationRule(
            field="test_field",
            rule_type=ValidationType.TYPE,
            expected_type="bool"
        )
        assert rule.validate(True) is None
        assert rule.validate(False) is None

    def test_type_list_passes(self):
        """Test type check passes for valid list"""
        rule = ValidationRule(
            field="test_field",
            rule_type=ValidationType.TYPE,
            expected_type="list"
        )
        result = rule.validate([1, 2, 3])
        assert result is None

    def test_type_dict_passes(self):
        """Test type check passes for valid dict"""
        rule = ValidationRule(
            field="test_field",
            rule_type=ValidationType.TYPE,
            expected_type="dict"
        )
        result = rule.validate({"key": "value"})
        assert result is None


class TestRangeRule:
    """Test RANGE validation rule"""

    def test_range_within_bounds(self):
        """Test range check passes when value is within bounds"""
        rule = ValidationRule(
            field="test_field",
            rule_type=ValidationType.RANGE,
            min=0,
            max=100
        )
        assert rule.validate(50) is None
        assert rule.validate(0) is None
        assert rule.validate(100) is None

    def test_range_below_minimum(self):
        """Test range check fails when value is below minimum"""
        rule = ValidationRule(
            field="test_field",
            rule_type=ValidationType.RANGE,
            min=0,
            max=100
        )
        result = rule.validate(-1)
        assert isinstance(result, ValidationError)
        assert "must be >= 0" in result.message

    def test_range_above_maximum(self):
        """Test range check fails when value is above maximum"""
        rule = ValidationRule(
            field="test_field",
            rule_type=ValidationType.RANGE,
            min=0,
            max=100
        )
        result = rule.validate(101)
        assert isinstance(result, ValidationError)
        assert "must be <= 100" in result.message

    def test_range_only_minimum(self):
        """Test range check with only minimum constraint"""
        rule = ValidationRule(
            field="test_field",
            rule_type=ValidationType.RANGE,
            min=10
        )
        assert rule.validate(10) is None
        assert rule.validate(100) is None
        result = rule.validate(5)
        assert isinstance(result, ValidationError)

    def test_range_only_maximum(self):
        """Test range check with only maximum constraint"""
        rule = ValidationRule(
            field="test_field",
            rule_type=ValidationType.RANGE,
            max=100
        )
        assert rule.validate(50) is None
        assert rule.validate(0) is None
        result = rule.validate(101)
        assert isinstance(result, ValidationError)

    def test_range_with_float(self):
        """Test range check with float values"""
        rule = ValidationRule(
            field="test_field",
            rule_type=ValidationType.RANGE,
            min=0.0,
            max=1.0
        )
        assert rule.validate(0.5) is None
        assert rule.validate(0.0) is None
        assert rule.validate(1.0) is None

    def test_range_with_invalid_type(self):
        """Test range check fails with non-numeric value"""
        rule = ValidationRule(
            field="test_field",
            rule_type=ValidationType.RANGE,
            min=0,
            max=100
        )
        result = rule.validate("not a number")
        assert isinstance(result, ValidationError)


class TestRegexRule:
    """Test REGEX validation rule"""

    def test_regex_matches(self):
        """Test regex passes when pattern matches"""
        rule = ValidationRule(
            field="test_field",
            rule_type=ValidationType.REGEX,
            pattern=r"^[A-Z0-9-]+$"
        )
        assert rule.validate("ABC-123") is None
        assert rule.validate("TEST") is None

    def test_regex_no_match(self):
        """Test regex fails when pattern doesn't match"""
        rule = ValidationRule(
            field="test_field",
            rule_type=ValidationType.REGEX,
            pattern=r"^[A-Z0-9-]+$"
        )
        result = rule.validate("abc-123")  # lowercase not allowed
        assert isinstance(result, ValidationError)
        assert "does not match required pattern" in result.message

    def test_regex_email_pattern(self):
        """Test regex with email pattern"""
        rule = ValidationRule(
            field="email",
            rule_type=ValidationType.REGEX,
            pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        )
        assert rule.validate("user@example.com") is None
        result = rule.validate("invalid-email")
        assert isinstance(result, ValidationError)

    def test_regex_phone_pattern(self):
        """Test regex with phone number pattern"""
        rule = ValidationRule(
            field="phone",
            rule_type=ValidationType.REGEX,
            pattern=r"^\d{3}-\d{3}-\d{4}$"
        )
        assert rule.validate("555-123-4567") is None
        result = rule.validate("5551234567")  # missing dashes
        assert isinstance(result, ValidationError)


class TestLengthRule:
    """Test LENGTH validation rule"""

    def test_length_within_bounds(self):
        """Test length check passes when within bounds"""
        rule = ValidationRule(
            field="test_field",
            rule_type=ValidationType.LENGTH,
            min=2,
            max=10
        )
        assert rule.validate("hello") is None
        assert rule.validate([1, 2, 3]) is None

    def test_length_too_short(self):
        """Test length check fails when too short"""
        rule = ValidationRule(
            field="test_field",
            rule_type=ValidationType.LENGTH,
            min=5,
            max=10
        )
        result = rule.validate("hi")
        assert isinstance(result, ValidationError)
        assert "must have length >= 5" in result.message

    def test_length_too_long(self):
        """Test length check fails when too long"""
        rule = ValidationRule(
            field="test_field",
            rule_type=ValidationType.LENGTH,
            min=2,
            max=5
        )
        result = rule.validate("toolong")
        assert isinstance(result, ValidationError)
        assert "must have length <= 5" in result.message

    def test_length_only_minimum(self):
        """Test length check with only minimum constraint"""
        rule = ValidationRule(
            field="test_field",
            rule_type=ValidationType.LENGTH,
            min=3
        )
        assert rule.validate("hello") is None
        result = rule.validate("hi")
        assert isinstance(result, ValidationError)

    def test_length_with_list(self):
        """Test length check with list"""
        rule = ValidationRule(
            field="test_field",
            rule_type=ValidationType.LENGTH,
            min=2,
            max=5
        )
        assert rule.validate([1, 2, 3]) is None
        result = rule.validate([1, 2, 3, 4, 5, 6])
        assert isinstance(result, ValidationError)


class TestEnumRule:
    """Test ENUM validation rule"""

    def test_enum_valid_value(self):
        """Test enum passes with valid value"""
        rule = ValidationRule(
            field="test_field",
            rule_type=ValidationType.ENUM,
            allowed_values=["ASO", "Fully Insured", "Self-Funded"]
        )
        assert rule.validate("ASO") is None
        assert rule.validate("Self-Funded") is None

    def test_enum_invalid_value(self):
        """Test enum fails with invalid value"""
        rule = ValidationRule(
            field="test_field",
            rule_type=ValidationType.ENUM,
            allowed_values=["ASO", "Fully Insured", "Self-Funded"]
        )
        result = rule.validate("Invalid")
        assert isinstance(result, ValidationError)
        assert "must be one of" in result.message

    def test_enum_with_numbers(self):
        """Test enum with numeric values"""
        rule = ValidationRule(
            field="test_field",
            rule_type=ValidationType.ENUM,
            allowed_values=[1, 2, 3, 4, 5]
        )
        assert rule.validate(3) is None
        result = rule.validate(10)
        assert isinstance(result, ValidationError)


class TestDateFormatRule:
    """Test DATE_FORMAT validation rule"""

    def test_date_format_valid(self):
        """Test date format passes with valid date"""
        rule = ValidationRule(
            field="test_field",
            rule_type=ValidationType.DATE_FORMAT,
            format="%Y-%m-%d"
        )
        assert rule.validate("2024-01-15") is None
        assert rule.validate("2024-12-31") is None

    def test_date_format_invalid(self):
        """Test date format fails with invalid date"""
        rule = ValidationRule(
            field="test_field",
            rule_type=ValidationType.DATE_FORMAT,
            format="%Y-%m-%d"
        )
        result = rule.validate("01/15/2024")  # wrong format
        assert isinstance(result, ValidationError)
        assert "must be in format" in result.message

    def test_date_format_custom(self):
        """Test date format with custom format"""
        rule = ValidationRule(
            field="test_field",
            rule_type=ValidationType.DATE_FORMAT,
            format="%m/%d/%Y"
        )
        assert rule.validate("01/15/2024") is None
        result = rule.validate("2024-01-15")
        assert isinstance(result, ValidationError)

    def test_date_format_invalid_date_values(self):
        """Test date format fails with invalid date values"""
        rule = ValidationRule(
            field="test_field",
            rule_type=ValidationType.DATE_FORMAT,
            format="%Y-%m-%d"
        )
        result = rule.validate("2024-13-01")  # month 13 doesn't exist
        assert isinstance(result, ValidationError)


class TestCustomRule:
    """Test CUSTOM validation rule"""

    def test_custom_passes(self):
        """Test custom rule passes when validator returns True"""
        def is_even(value):
            return value % 2 == 0

        rule = ValidationRule(
            field="test_field",
            rule_type=ValidationType.CUSTOM,
            validator=is_even
        )
        assert rule.validate(4) is None
        assert rule.validate(100) is None

    def test_custom_fails(self):
        """Test custom rule fails when validator returns False"""
        def is_even(value):
            return value % 2 == 0

        rule = ValidationRule(
            field="test_field",
            rule_type=ValidationType.CUSTOM,
            validator=is_even
        )
        result = rule.validate(3)
        assert isinstance(result, ValidationError)

    def test_custom_with_error_message(self):
        """Test custom rule with custom error message"""
        def validate_policy_number(value):
            if len(value) < 5:
                return "Policy number must be at least 5 characters"
            return True

        rule = ValidationRule(
            field="policy_number",
            rule_type=ValidationType.CUSTOM,
            validator=validate_policy_number
        )
        result = rule.validate("ABC")
        assert isinstance(result, ValidationError)
        assert "must be at least 5 characters" in result.message


class TestSeverityLevels:
    """Test validation severity levels"""

    def test_error_severity(self):
        """Test error severity"""
        rule = ValidationRule(
            field="test_field",
            rule_type=ValidationType.REQUIRED,
            severity=Severity.ERROR
        )
        result = rule.validate(None)
        assert isinstance(result, ValidationError)
        assert result.severity == Severity.ERROR

    def test_warning_severity(self):
        """Test warning severity"""
        rule = ValidationRule(
            field="test_field",
            rule_type=ValidationType.REQUIRED,
            severity=Severity.WARNING
        )
        result = rule.validate(None)
        assert isinstance(result, ValidationError)
        assert result.severity == Severity.WARNING

    def test_info_severity(self):
        """Test info severity"""
        rule = ValidationRule(
            field="test_field",
            rule_type=ValidationType.REQUIRED,
            severity=Severity.INFO
        )
        result = rule.validate(None)
        assert isinstance(result, ValidationError)
        assert result.severity == Severity.INFO


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
