"""
Configuration utilities for Obelisk.

This module provides functions for loading and managing configuration
from various sources, including files and environment variables.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


def get_config_path() -> Optional[str]:
    """
    Get the path to the configuration file.
    
    Checks for configuration in the following order:
    1. Environment variable OBELISK_CONFIG
    2. User config at ~/.config/obelisk/config.yaml
    3. System config at /etc/obelisk/config.yaml
    4. Local config at ./obelisk.yaml
    
    Returns:
        The path to the configuration file, or None if not found.
    """
    # Check environment variable
    if "OBELISK_CONFIG" in os.environ:
        return os.environ["OBELISK_CONFIG"]
    
    # Check user config
    user_config = os.path.expanduser("~/.config/obelisk/config.yaml")
    if os.path.exists(user_config):
        return user_config
    
    # Check system config
    system_config = "/etc/obelisk/config.yaml"
    if os.path.exists(system_config):
        return system_config
    
    # Check local config
    local_config = os.path.join(os.getcwd(), "obelisk.yaml")
    if os.path.exists(local_config):
        return local_config
    
    return None


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from a YAML file and apply environment overrides.
    
    Args:
        config_path: Optional path to the configuration file. If not provided,
                    will try to find a config file using get_config_path().
    
    Returns:
        A dictionary containing the configuration.
    """
    config = {}
    
    # If no path provided, try to find one
    if config_path is None:
        config_path = get_config_path()
    
    # Load config from file if it exists
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                file_config = yaml.safe_load(f)
                if file_config:
                    config = file_config
        except (yaml.YAMLError, IOError) as e:
            print(f"Error loading config from {config_path}: {e}")
    
    # Apply environment variable overrides
    # Environment variables in format OBELISK_KEY=value or OBELISK_SECTION__KEY=value
    env_overrides = {}
    for env_var, env_value in os.environ.items():
        if env_var.startswith("OBELISK_"):
            # Remove prefix and convert to lowercase
            key_path = env_var[8:].lower()
            
            # Handle nested keys (using double underscore as separator)
            if "__" in key_path:
                # Split into sections
                sections = key_path.split("__")
                
                # Start with a reference to the env_overrides dict
                current = env_overrides
                
                # Create nested dictionaries for each section except the last
                for section in sections[:-1]:
                    if section not in current:
                        current[section] = {}
                    current = current[section]
                
                # Set the value for the last section
                current[sections[-1]] = _convert_value(env_value)
            else:
                # Simple key
                env_overrides[key_path] = _convert_value(env_value)
    
    # Merge environment overrides with file config
    if env_overrides:
        config = deep_merge(config, env_overrides)
    
    return config


def _convert_value(value: str) -> Any:
    """
    Convert a string value to the appropriate type.
    
    Args:
        value: The string value to convert.
    
    Returns:
        The converted value.
    """
    # Try to convert to boolean
    if value.lower() in ("true", "yes", "1", "on"):
        return True
    if value.lower() in ("false", "no", "0", "off"):
        return False
    
    # Try to convert to integer
    try:
        return int(value)
    except ValueError:
        pass
    
    # Try to convert to float
    try:
        return float(value)
    except ValueError:
        pass
    
    # Return as string
    return value


def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries.
    
    Values in override will overwrite values in base, except for dictionaries
    which will be recursively merged.
    
    Args:
        base: The base dictionary.
        override: The dictionary to merge on top of base.
    
    Returns:
        A new dictionary with the merged values.
    """
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result