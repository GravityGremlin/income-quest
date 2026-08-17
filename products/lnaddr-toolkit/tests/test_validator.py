"""Tests for lnaddr-toolkit validator module."""

import pytest

from lnaddr_toolkit.validator import (
    validate_lightning_address,
    parse_lightning_address,
    is_valid_lightning_address,
)
from lnaddr_toolkit.exceptions import ValidationError


class TestValidateLightningAddress:
    """Tests for validate_lightning_address function."""

    def test_valid_addresses(self):
        """Test various valid Lightning Address formats."""
        valid = [
            "user@domain.com",
            "alice@wallet.example.com",
            "user.name@domain.com",
            "user_name@domain.com",
            "user-name@domain.com",
            "user123@domain.com",
            "a@b.co",
            "user@sub.domain.com",
            "user@domain.io",
            "user@domain.xyz",
        ]
        for addr in valid:
            assert validate_lightning_address(addr) is True
            assert is_valid_lightning_address(addr) is True

    def test_invalid_addresses(self):
        """Test various invalid Lightning Address formats."""
        invalid = [
            "",  # empty
            "user",  # no @
            "@domain.com",  # no local part
            "user@",  # no domain
            "user@domain",  # no TLD
            "user@.com",  # empty subdomain
            "user@domain..com",  # double dot
            "user@-domain.com",  # leading hyphen
            "user@domain-.com",  # trailing hyphen
            ".user@domain.com",  # leading dot in local
            "user.@domain.com",  # trailing dot in local
            "user..name@domain.com",  # consecutive dots in local
            "user@domain.c",  # TLD too short
            "user name@domain.com",  # space in local
            "user@domain .com",  # space in domain
            "user@domain.com ",  # trailing space
            " user@domain.com",  # leading space
        ]
        for addr in invalid:
            assert is_valid_lightning_address(addr) is False
            with pytest.raises(ValidationError):
                validate_lightning_address(addr)

    def test_case_insensitive(self):
        """Test that validation is case-insensitive."""
        assert validate_lightning_address("USER@DOMAIN.COM") is True
        assert validate_lightning_address("User@Domain.Com") is True

    def test_strips_whitespace(self):
        """Test that surrounding whitespace is stripped."""
        assert validate_lightning_address("  user@domain.com  ") is True


class TestParseLightningAddress:
    """Tests for parse_lightning_address function."""

    def test_valid_parsing(self):
        """Test parsing valid addresses."""
        assert parse_lightning_address("user@domain.com") == ("user", "domain.com")
        assert parse_lightning_address("alice@wallet.example.com") == ("alice", "wallet.example.com")
        assert parse_lightning_address("USER@DOMAIN.COM") == ("user", "domain.com")

    def test_invalid_raises(self):
        """Test that invalid addresses raise ValidationError."""
        with pytest.raises(ValidationError):
            parse_lightning_address("invalid")
        with pytest.raises(ValidationError):
            parse_lightning_address("@domain.com")


class TestIsValidLightningAddress:
    """Tests for is_valid_lightning_address function."""

    def test_returns_bool_no_exception(self):
        """Test that function returns bool and never raises."""
        assert is_valid_lightning_address("user@domain.com") is True
        assert is_valid_lightning_address("invalid") is False
        assert is_valid_lightning_address("") is False
        assert is_valid_lightning_address(None) is False  # type: ignore
        assert is_valid_lightning_address(123) is False  # type: ignore