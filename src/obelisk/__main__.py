"""
Main entry point for the Obelisk CLI.

This allows the package to be executed directly with:
python -m src.obelisk
"""

from src.obelisk.cli.commands import main

if __name__ == "__main__":
    main()