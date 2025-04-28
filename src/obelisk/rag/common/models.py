"""
Model abstraction layer for the Obelisk RAG system.

This module provides a common interface for different model providers,
abstracting away the specific implementation details and allowing for
seamless switching between providers.
"""

import logging
from typing import Dict, Any, Optional, List, Union

logger = logging.getLogger(__name__)

# Initial placeholder for model abstractions
# Implementation details will be added in subsequent commits