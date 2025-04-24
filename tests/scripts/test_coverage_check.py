#!/usr/bin/env python3
"""
Script to check test coverage for the src-layout pattern.

This script scans the source files and checks which ones have corresponding tests.
"""

import os
import glob
from pathlib import Path


def scan_source_files():
    """Scan source files in the src-layout pattern."""
    src_dir = Path("/workspaces/obelisk/src")
    source_files = []
    
    for py_file in sorted(src_dir.glob("**/*.py")):
        if "__pycache__" not in str(py_file):
            source_files.append(py_file)
    
    return source_files


def scan_test_files():
    """Scan test files."""
    test_dir = Path("/workspaces/obelisk/tests")
    test_files = []
    
    for py_file in sorted(test_dir.glob("**/*.py")):
        if "__pycache__" not in str(py_file) and "__init__.py" not in str(py_file):
            test_files.append(py_file)
    
    return test_files


def extract_module_name(file_path):
    """Extract module name from file path."""
    parts = str(file_path).split("/src/")
    if len(parts) < 2:
        return None
    
    module_path = parts[1].replace("/", ".").replace(".py", "")
    return module_path


def check_test_coverage(test_files, source_modules):
    """Check if source modules are covered by tests."""
    covered_modules = set()
    coverage_details = {}
    
    # Map from simple module name to full module path
    module_map = {}
    for module in source_modules:
        parts = module.split('.')
        if len(parts) > 1:
            simple_name = parts[-1]
            module_map[simple_name] = module
    
    for test_file in test_files:
        test_file_name = os.path.basename(test_file)
        
        # Check for test files that match module names
        for simple_name, full_module in module_map.items():
            if f"test_{simple_name}" in test_file_name:
                covered_modules.add(full_module)
                coverage_details[full_module] = str(test_file)
        
        # Check for imports
        with open(test_file, "r") as f:
            content = f.read()
            
            for module in source_modules:
                if f"from src.{module}" in content or f"import src.{module}" in content:
                    covered_modules.add(module)
                    coverage_details[module] = str(test_file)
                # Also check for old-style imports without src.
                elif f"from {module}" in content or f"import {module}" in content:
                    covered_modules.add(module)
                    coverage_details[module] = str(test_file)
    
    return covered_modules, coverage_details


def main():
    """Main function."""
    source_files = scan_source_files()
    test_files = scan_test_files()
    
    source_modules = [extract_module_name(f) for f in source_files]
    source_modules = [m for m in source_modules if m]  # Filter out None values
    
    covered_modules, coverage_details = check_test_coverage(test_files, source_modules)
    
    print(f"Total source modules: {len(source_modules)}")
    print(f"Modules with test coverage: {len(covered_modules)}")
    print(f"Coverage percentage: {len(covered_modules) / len(source_modules) * 100:.2f}%")
    
    print("\nTest coverage details:")
    for module in sorted(covered_modules):
        print(f"  - {module}: {coverage_details[module]}")
    
    print("\nUntested modules:")
    untested = set(source_modules) - covered_modules
    for module in sorted(untested):
        print(f"  - {module}")


if __name__ == "__main__":
    main()