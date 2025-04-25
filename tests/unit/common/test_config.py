"""Unit tests for the Obelisk common configuration module."""

import os
import pytest
from unittest.mock import patch, mock_open
from pathlib import Path

from src.obelisk.common.config import load_config, get_config_path, deep_merge, _convert_value


@pytest.fixture
def mock_yaml_file(tmp_path):
    """Create a mock YAML configuration file."""
    config_file = tmp_path / "config.yaml"
    with open(config_file, "w") as f:
        f.write("""
app_name: Obelisk
version: 0.1.0
debug: false
paths:
  vault: ./vault
  data: ./data
""")
    return str(config_file)


def test_get_config_path():
    """Test getting the configuration path."""
    # Test with environment variable
    with patch.dict(os.environ, {"OBELISK_CONFIG": "/path/to/config.yaml"}):
        path = get_config_path()
        assert path == "/path/to/config.yaml"
    
    # Test default paths
    with patch.dict(os.environ, {}, clear=True):
        with patch("os.path.exists") as mock_exists:
            # No config files exist
            mock_exists.return_value = False
            path = get_config_path()
            assert path is None
            
            # User config exists
            mock_exists.side_effect = lambda p: "/.config/obelisk/config.yaml" in p
            path = get_config_path()
            assert "/.config/obelisk/config.yaml" in path
            
            # System config exists
            mock_exists.side_effect = lambda p: "/etc/obelisk/config.yaml" in p
            path = get_config_path()
            assert "/etc/obelisk/config.yaml" in path
            
            # Local config exists
            mock_exists.side_effect = lambda p: p.endswith("obelisk.yaml")
            path = get_config_path()
            assert path.endswith("obelisk.yaml")


def test_load_config(mock_yaml_file):
    """Test loading configuration from a YAML file."""
    # Test loading from a path
    config = load_config(mock_yaml_file)
    assert config["app_name"] == "Obelisk"
    assert config["version"] == "0.1.0"
    assert config["debug"] is False
    assert "paths" in config
    
    # Test with environment variable overrides
    with patch.dict(os.environ, {"OBELISK_DEBUG": "true"}):
        config = load_config(mock_yaml_file)
        assert config["debug"] is True
    
    # Test with non-existent file
    config = load_config("/non/existent/path.yaml")
    assert config == {}
    
    # Test with nested environment variable overrides
    with patch.dict(os.environ, {"OBELISK_PATHS__VAULT": "/custom/vault"}):
        config = load_config(mock_yaml_file)
        assert config["paths"]["vault"] == "/custom/vault"
        assert config["paths"]["data"] == "./data"  # Original value preserved


def test_convert_value():
    """Test conversion of string values to appropriate types."""
    # Test boolean conversion
    assert _convert_value("true") is True
    assert _convert_value("yes") is True
    assert _convert_value("1") is True
    assert _convert_value("on") is True
    assert _convert_value("TRUE") is True
    
    assert _convert_value("false") is False
    assert _convert_value("no") is False
    assert _convert_value("0") is False
    assert _convert_value("off") is False
    assert _convert_value("FALSE") is False
    
    # Test integer conversion
    assert _convert_value("42") == 42
    assert _convert_value("-10") == -10
    
    # Test float conversion
    assert _convert_value("3.14") == 3.14
    assert _convert_value("-2.5") == -2.5
    
    # Test string (no conversion)
    assert _convert_value("hello") == "hello"
    assert _convert_value("1.2.3") == "1.2.3"  # Not a valid float
    

def test_deep_merge():
    """Test deep merging of dictionaries."""
    base = {
        "a": 1,
        "b": {
            "c": 2,
            "d": 3
        },
        "e": [1, 2, 3]
    }
    
    override = {
        "b": {
            "d": 4,
            "f": 5
        },
        "e": [4, 5, 6],
        "g": 6
    }
    
    result = deep_merge(base, override)
    
    # Check values
    assert result["a"] == 1
    assert result["b"]["c"] == 2
    assert result["b"]["d"] == 4
    assert result["b"]["f"] == 5
    assert result["e"] == [4, 5, 6]  # Lists are replaced, not merged
    assert result["g"] == 6
    
    # Check that the original dictionaries were not modified
    assert base["b"]["d"] == 3
    assert "f" not in base["b"]
    assert base["e"] == [1, 2, 3]
    assert "g" not in base