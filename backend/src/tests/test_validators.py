from src.domain.constants import UNKNOWN_ACCOUNT
from src.domain.validators import validate_clabe


class TestValidateClabe:
    def test_valid_18_digits(self):
        assert validate_clabe("123456789012345678") is True

    def test_empty_string(self):
        assert validate_clabe("") is False

    def test_unknown_account_constant(self):
        assert validate_clabe(UNKNOWN_ACCOUNT) is False

    def test_17_digits(self):
        assert validate_clabe("12345678901234567") is False

    def test_19_digits(self):
        assert validate_clabe("1234567890123456789") is False

    def test_contains_letters(self):
        assert validate_clabe("12345678901234567a") is False
