#!/usr/bin/env python3
"""Validate code examples in documentation files."""
import re
import sys
import ast
from pathlib import Path
from typing import List, Tuple

class DocValidator:
    """Validates code blocks in markdown documentation."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        
    def validate_file(self, filepath: Path) -> Tuple[int, int]:
        """Validate a single markdown file."""
        content = filepath.read_text()
        
        # Extract code blocks
        python_blocks = re.findall(r'```python\n(.*?)\n```', content, re.DOTALL)
        bash_blocks = re.findall(r'```bash\n(.*?)\n```', content, re.DOTALL)
        
        errors = 0
        warnings = 0
        
        # Validate Python blocks
        for i, code in enumerate(python_blocks):
            try:
                # Check for syntax errors
                ast.parse(code)
            except SyntaxError as e:
                self.errors.append(f"{filepath}:python-block-{i+1}: {e}")
                errors += 1
                
            # Check for common issues
            if 'ChromaDB' in code or 'chroma' in code:
                self.warnings.append(f"{filepath}:python-block-{i+1}: Contains ChromaDB reference")
                warnings += 1
                
        # Validate Bash blocks
        for i, code in enumerate(bash_blocks):
            # Check for outdated commands
            if 'CHROMA_' in code:
                self.warnings.append(f"{filepath}:bash-block-{i+1}: Contains ChromaDB environment variable")
                warnings += 1
            
            if '/api/generate' in code or '/v1/litellm' in code:
                self.warnings.append(f"{filepath}:bash-block-{i+1}: Contains outdated API endpoint")
                warnings += 1
                
        return errors, warnings
    
    def check_references(self, filepath: Path) -> int:
        """Check for outdated references in documentation."""
        content = filepath.read_text()
        issues = 0
        
        # Check for ChromaDB references
        if 'ChromaDB' in content:
            count = content.count('ChromaDB')
            self.warnings.append(f"{filepath}: Contains {count} ChromaDB references")
            issues += count
            
        # Check for outdated embedding model
        if 'mxbai-embed-large' in content:
            count = content.count('mxbai-embed-large')
            self.warnings.append(f"{filepath}: Contains {count} outdated embedding model references")
            issues += count
            
        # Check for 1024 dimensions
        if re.search(r'1024.*dim|1024-dim', content):
            self.warnings.append(f"{filepath}: References 1024 dimensions (should be 3072)")
            issues += 1
            
        return issues
    
    def validate_all(self, directory: Path) -> None:
        """Validate all markdown files in directory."""
        total_errors = 0
        total_warnings = 0
        files_checked = 0
        
        for md_file in directory.rglob('*.md'):
            # Skip TASK files and historical references
            if 'TASK' in md_file.name or 'historical' in str(md_file):
                continue
                
            files_checked += 1
            errors, warnings = self.validate_file(md_file)
            total_errors += errors
            total_warnings += warnings
            
            # Check general references
            ref_issues = self.check_references(md_file)
            total_warnings += ref_issues
            
        # Print summary
        print(f"\n=== Documentation Validation Report ===")
        print(f"Files checked: {files_checked}")
        print(f"Errors found: {total_errors}")
        print(f"Warnings found: {total_warnings}")
        
        if self.errors:
            print("\n❌ Errors:")
            for error in self.errors:
                print(f"  {error}")
                
        if self.warnings:
            print("\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"  {warning}")
                
        # Exit with error code if issues found
        if total_errors > 0:
            sys.exit(1)

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate documentation files')
    parser.add_argument('path', nargs='?', default='vault', 
                       help='Path to documentation directory (default: vault)')
    args = parser.parse_args()
    
    validator = DocValidator()
    validator.validate_all(Path(args.path))

if __name__ == '__main__':
    main()