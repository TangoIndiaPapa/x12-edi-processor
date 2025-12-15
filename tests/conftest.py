"""Test configuration and fixtures."""

import pytest
from pathlib import Path


@pytest.fixture
def fixtures_dir():
    """Return path to fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_277_content(fixtures_dir):
    """Load valid X12 277 Claims Status Response from LinuxForHealth test suite."""
    file_path = fixtures_dir / "277_claim_level_status.x12"
    return file_path.read_text(encoding='utf-8')


@pytest.fixture
def sample_835_medicare(fixtures_dir):
    """Load valid X12 835 Medicare Part A Payment from LinuxForHealth test suite."""
    file_path = fixtures_dir / "835_medicare_part_a.x12"
    return file_path.read_text(encoding='utf-8')


@pytest.fixture
def sample_835_managed_care(fixtures_dir):
    """Load valid X12 835 Managed Care Payment from LinuxForHealth test suite."""
    file_path = fixtures_dir / "835_managed_care.x12"
    return file_path.read_text(encoding='utf-8')


# Legacy fixture for backward compatibility
@pytest.fixture
def sample_835_content(sample_835_medicare):
    """Alias for sample_835_medicare for backward compatibility."""
    return sample_835_medicare


@pytest.fixture
def temp_x12_file(tmp_path, sample_277_content):
    """Create temporary X12 file for testing."""
    file_path = tmp_path / "test.x12"
    file_path.write_text(sample_277_content)
    return file_path


@pytest.fixture
def mock_s3_bucket():
    """Mock S3 bucket name."""
    return "test-edi-bucket"


@pytest.fixture
def mock_s3_key():
    """Mock S3 object key."""
    return "input/test.x12"
