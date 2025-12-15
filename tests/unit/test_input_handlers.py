"""Unit tests for input handlers."""

import pytest
from src.input.local_input import LocalInput
from src.core.exceptions import InputError


class TestLocalInput:
    """Tests for local file input handler."""
    
    def test_read_valid_file(self, temp_x12_file):
        """Test reading valid local file."""
        handler = LocalInput(str(temp_x12_file))
        content = handler.read()
        
        assert content is not None
        assert len(content) > 0
        assert "ISA" in content
    
    def test_validate_existing_file(self, temp_x12_file):
        """Test validation of existing file."""
        handler = LocalInput(str(temp_x12_file))
        assert handler.validate_source() is True
    
    def test_validate_nonexistent_file(self):
        """Test validation of non-existent file."""
        handler = LocalInput("/nonexistent/file.x12")
        
        with pytest.raises(InputError):
            handler.validate_source()
    
    def test_get_metadata(self, temp_x12_file):
        """Test getting file metadata."""
        handler = LocalInput(str(temp_x12_file))
        metadata = handler.get_metadata()
        
        assert "path" in metadata
        assert "size" in metadata
        assert metadata["size"] > 0
