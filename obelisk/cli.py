"""
Obelisk CLI tool to convert Obsidian vaults to MkDocs sites.
"""

import argparse
import os
import sys
import shutil
import subprocess
from pathlib import Path

from . import __version__


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Convert Obsidian vault to MkDocs Material Theme site."
    )
    parser.add_argument(
        "--version", action="version", version=f"Obelisk {__version__}"
    )
    parser.add_argument(
        "--vault", 
        type=str, 
        help="Path to Obsidian vault directory",
        default="vault"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        help="Output directory for the generated site",
        default="site"
    )
    parser.add_argument(
        "--serve", 
        action="store_true", 
        help="Start a development server after building"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        help="Port to use for the development server",
        default=8000
    )
    
    args = parser.parse_args()
    
    print(f"Obelisk {__version__} - Obsidian to MkDocs converter")
    
    # Ensure vault directory exists
    vault_path = Path(args.vault)
    if not vault_path.exists() or not vault_path.is_dir():
        sys.exit(f"Error: Vault directory '{args.vault}' not found or is not a directory")
    
    # Build the site
    build_cmd = ["mkdocs", "build", "-d", args.output]
    try:
        subprocess.run(build_cmd, check=True)
        print(f"✅ Site built successfully in '{args.output}'")
    except subprocess.CalledProcessError:
        sys.exit("Error: Failed to build the site")
    
    # Serve if requested
    if args.serve:
        serve_cmd = ["mkdocs", "serve", "--dev-addr", f"localhost:{args.port}"]
        try:
            subprocess.run(serve_cmd)
        except KeyboardInterrupt:
            print("\nDevelopment server stopped")
        except subprocess.CalledProcessError:
            sys.exit("Error: Failed to start development server")


if __name__ == "__main__":
    main()