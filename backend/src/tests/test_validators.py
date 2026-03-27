from src.domain.postprocessors.mexican_bank_statement import (
    UNKNOWN_ACCOUNT,
    validate_clabe,
    verify_clabe_checksum,
)


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


class TestVerifyClabeChecksum:
    def test_known_valid_clabe_banorte(self):
        # Real CLABE format: 072 691 00844421773 3
        assert verify_clabe_checksum("072691008444217733") is True

    def test_invalid_checksum(self):
        # Flip last digit of a valid CLABE
        assert verify_clabe_checksum("072691008444217734") is False

    def test_wrong_digits_from_extraction(self):
        # The incorrectly extracted CLABE from the user's case
        assert verify_clabe_checksum("072691008442177313") is False

    def test_not_18_digits(self):
        assert verify_clabe_checksum("1234567890") is False

    def test_empty_string(self):
        assert verify_clabe_checksum("") is False

    def test_unknown_account(self):
        assert verify_clabe_checksum(UNKNOWN_ACCOUNT) is False

    def test_all_zeros_bank(self):
        # 002010077777777771 — compute manually
        digits = [0, 0, 2, 0, 1, 0, 0, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7]
        weights = [3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7]
        total = sum((d * w) % 10 for d, w in zip(digits, weights))
        check = (10 - total % 10) % 10
        clabe = "00201007777777777" + str(check)
        assert verify_clabe_checksum(clabe) is True
