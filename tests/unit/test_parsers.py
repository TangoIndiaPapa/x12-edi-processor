"""Unit tests for X12 parsers."""

import pytest
from src.parsers.x12_277_parser import X12_277_Parser
from src.parsers.x12_835_parser import X12_835_Parser
from src.core.exceptions import X12ParseError


class TestX12_277_Parser:
    """Tests for X12 277 parser."""
    
    def test_parse_valid_277(self, sample_277_content):
        """Test parsing valid 277 content."""
        parser = X12_277_Parser()
        result = parser.parse(sample_277_content)
        
        assert result["transaction_type"] == "277"
        assert result["version"] == "005010X212"
        assert len(result["transactions"]) > 0
    
    def test_validate_parsed_277(self, sample_277_content):
        """Test validation of parsed 277 data."""
        parser = X12_277_Parser()
        parsed_data = parser.parse(sample_277_content)
        
        errors = parser.validate(parsed_data)
        assert isinstance(errors, list)


class TestX12_835_Parser:
    """Tests for X12 835 parser."""
    
    def test_parse_valid_835(self, sample_835_content):
        """Test parsing valid 835 content."""
        parser = X12_835_Parser()
        result = parser.parse(sample_835_content)
        
        assert result["transaction_type"] == "835"
        assert result["version"] == "005010X221A1"
        assert len(result["transactions"]) > 0
    
    def test_validate_parsed_835(self, sample_835_content):
        """Test validation of parsed 835 data."""
        parser = X12_835_Parser()
        parsed_data = parser.parse(sample_835_content)
        
        errors = parser.validate(parsed_data)
        assert isinstance(errors, list)
