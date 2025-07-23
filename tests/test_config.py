import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from mosaico.config import Settings


@pytest.fixture
def system_temp_dir():
    """Return the resolved system temp directory for consistent comparison."""
    return str(Path(tempfile.gettempdir()).resolve())


def test_resolved_temp_dir_uses_custom_when_valid(tmp_path):
    """Test that resolved_temp_dir uses custom temp_dir when it exists and is writable."""
    custom_temp = tmp_path / "custom_temp"
    custom_temp.mkdir()

    settings = Settings(temp_dir=str(custom_temp))
    assert settings.resolved_temp_dir == str(custom_temp)


def test_resolved_temp_dir_falls_back_when_custom_invalid(tmp_path, system_temp_dir):
    """Test that resolved_temp_dir falls back when custom temp_dir doesn't exist."""
    nonexistent_temp = tmp_path / "nonexistent"

    settings = Settings(temp_dir=str(nonexistent_temp))
    resolved = settings.resolved_temp_dir

    # Should fall back to system temp directory
    assert resolved == system_temp_dir


def test_resolved_temp_dir_falls_back_when_custom_not_writable(tmp_path, system_temp_dir, monkeypatch):
    """Test that resolved_temp_dir falls back when custom temp_dir is not writable."""
    readonly_temp = tmp_path / "readonly_temp"
    readonly_temp.mkdir()
    
    # Mock os.access to return False for write access to this specific directory
    original_access = os.access
    def mock_access(path, mode):
        if str(Path(path).resolve()) == str(readonly_temp.resolve()) and mode == os.W_OK:
            return False
        return original_access(path, mode)
    
    monkeypatch.setattr(os, "access", mock_access)

    settings = Settings(temp_dir=str(readonly_temp))
    resolved = settings.resolved_temp_dir

    # Should fall back to system temp directory
    assert resolved == system_temp_dir


def test_resolved_temp_dir_uses_system_temp_by_default(system_temp_dir):
    """Test that resolved_temp_dir uses system temp when no custom temp_dir is set."""
    settings = Settings()
    assert settings.resolved_temp_dir == system_temp_dir


def test_fallback_hierarchy_integration(tmp_path, monkeypatch, system_temp_dir):
    """Test fallback hierarchy with a real scenario using invalid custom temp."""
    # Create an invalid custom temp directory (doesn't exist)
    invalid_temp = tmp_path / "nonexistent_custom"

    # Mock environment to have invalid temp dir
    monkeypatch.setenv("MOSAICO_TEMP_DIR", str(invalid_temp))

    settings = Settings()
    resolved = settings.resolved_temp_dir

    # Should fall back to system temp directory since custom doesn't exist
    assert resolved == system_temp_dir


@patch("tempfile.gettempdir")
@patch("os.getcwd")
@patch("pathlib.Path.home")
@patch("os.access")
@patch("pathlib.Path.exists")
def test_runtime_error_when_no_writable_directory(mock_exists, mock_access, mock_home, mock_getcwd, mock_gettempdir):
    """Test that RuntimeError is raised when no writable directory is found."""
    # Mock all paths as inaccessible (using cross-platform compatible paths)
    mock_gettempdir.return_value = "/mock/temp"
    mock_getcwd.return_value = "/mock/current"
    mock_home.return_value = Path("/mock/home")

    mock_exists.return_value = False
    mock_access.return_value = False

    settings = Settings()

    with pytest.raises(RuntimeError, match="No writable temporary directory found"):
        settings.resolved_temp_dir


def test_temp_dir_environment_variable(tmp_path, monkeypatch):
    """Test that temp_dir can be set via environment variable."""
    custom_temp = tmp_path / "env_temp"
    custom_temp.mkdir()

    monkeypatch.setenv("MOSAICO_TEMP_DIR", str(custom_temp))

    settings = Settings()
    assert settings.temp_dir == str(custom_temp)
    assert settings.resolved_temp_dir == str(custom_temp)


def test_cross_platform_temp_directory_resolution():
    """Test that temp directory resolution works across different platforms."""
    settings = Settings()
    resolved_temp = settings.resolved_temp_dir

    # Should resolve to a valid directory path
    assert resolved_temp is not None
    assert isinstance(resolved_temp, str)
    assert len(resolved_temp) > 0

    # The resolved path should be writable
    temp_path = Path(resolved_temp)
    assert temp_path.exists()
    assert os.access(temp_path, os.W_OK)

    # Should be one of the expected fallback locations (resolve paths for Windows compatibility)
    expected_dirs = [
        str(Path(tempfile.gettempdir()).resolve()),  # System temp
        str(Path(os.getcwd()).resolve()),           # Current directory
        str(Path.home().resolve()),                 # User home
    ]
    assert resolved_temp in expected_dirs
