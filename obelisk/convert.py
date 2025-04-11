"""
Conversion utilities for transforming Obsidian files to MkDocs-compatible format.
"""

import os
import re
import shutil
from pathlib import Path


def process_obsidian_vault(vault_path, output_path="vault"):
    """
    Process an Obsidian vault directory and prepare it for MkDocs.
    
    Args:
        vault_path: Path to the Obsidian vault
        output_path: Path where processed files will be written
    
    Returns:
        The output path where files were written
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_path, exist_ok=True)
    
    # Process all markdown files in the vault
    for root, _, files in os.walk(vault_path):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, vault_path)
                output_file = os.path.join(output_path, relative_path)
                
                # Create subdirectories if needed
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                
                # Convert Obsidian-specific syntax to MkDocs compatible format
                convert_file(file_path, output_file)
            elif file.endswith((".png", ".jpg", ".jpeg", ".gif", ".svg")):
                # Copy images as-is
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, vault_path)
                output_file = os.path.join(output_path, relative_path)
                
                # Create subdirectories if needed
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                
                shutil.copy2(file_path, output_file)
    
    return output_path


def convert_file(input_path, output_path):
    """
    Convert an Obsidian markdown file to MkDocs compatible format.
    
    Args:
        input_path: Path to the input Obsidian markdown file
        output_path: Path where the converted file will be written
    """
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Convert Obsidian wiki links to markdown links
    content = convert_wiki_links(content)
    
    # Convert Obsidian callouts to admonitions
    content = convert_callouts(content)
    
    # Convert Obsidian comments to HTML comments
    content = convert_comments(content)
    
    # Write the converted content
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)


def convert_wiki_links(content):
    """
    Convert Obsidian wiki links to markdown links.
    
    Examples:
        [[Page Name]] -> [Page Name](Page%20Name.md)
        [[Page Name|Display Text]] -> [Display Text](Page%20Name.md)
    """
    # Regular expression for Obsidian wiki links
    wiki_link_pattern = r'\[\[(.*?)\]\]'
    
    def replace_wiki_link(match):
        link_text = match.group(1)
        
        # Handle aliases
        if '|' in link_text:
            page_name, display_text = link_text.split('|', 1)
        else:
            page_name = display_text = link_text
        
        # Handle sections
        if '#' in page_name:
            page_name, section = page_name.split('#', 1)
            url = f"{page_name.strip().replace(' ', '%20')}.md#{section.strip().lower().replace(' ', '-')}"
        else:
            url = f"{page_name.strip().replace(' ', '%20')}.md"
        
        return f"[{display_text.strip()}]({url})"
    
    return re.sub(wiki_link_pattern, replace_wiki_link, content)


def convert_callouts(content):
    """
    Convert Obsidian callouts to MkDocs admonitions.
    
    Example:
        > [!NOTE] Title
        > Content
        
        Becomes:
        
        !!! note "Title"
            Content
    """
    # Regular expression for Obsidian callouts
    callout_pattern = r'> \[!(.*?)\](.*?)\n((?:>.*\n)+)'
    
    def replace_callout(match):
        callout_type = match.group(1).strip().lower()
        title = match.group(2).strip()
        
        # Map Obsidian callout types to MkDocs admonition types
        admonition_types = {
            'note': 'note',
            'info': 'info',
            'tip': 'tip',
            'warning': 'warning',
            'danger': 'danger',
            'success': 'success',
            'question': 'question',
            'bug': 'bug',
            'example': 'example',
            'quote': 'quote',
            'abstract': 'abstract',
            'summary': 'summary',
        }
        
        admonition_type = admonition_types.get(callout_type, 'note')
        
        # Process content lines (remove the ">" prefix)
        content_lines = match.group(3).strip().split('\n')
        processed_content = '\n'.join([line[2:] if line.startswith('> ') else line for line in content_lines])
        
        # Format the admonition
        if title:
            return f'!!! {admonition_type} "{title}"\n    {processed_content.replace("\\n", "\\n    ")}\n'
        else:
            return f'!!! {admonition_type}\n    {processed_content.replace("\\n", "\\n    ")}\n'
    
    return re.sub(callout_pattern, replace_callout, content, flags=re.DOTALL)


def convert_comments(content):
    """
    Convert Obsidian comments to HTML comments.
    
    Example:
        %% Comment %% -> <!-- Comment -->
    """
    # Regular expression for Obsidian comments
    comment_pattern = r'%%(.*?)%%'
    
    def replace_comment(match):
        comment_text = match.group(1).strip()
        return f'<!-- {comment_text} -->'
    
    return re.sub(comment_pattern, replace_comment, content, flags=re.DOTALL)