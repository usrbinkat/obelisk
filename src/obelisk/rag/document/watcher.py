"""
Document watching for the Obelisk RAG system.

This module provides file system monitoring to detect changes in markdown files
and trigger processing of new or updated documents.
"""

import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

# Set up logging
logger = logging.getLogger(__name__)


class MarkdownWatcher(FileSystemEventHandler):
    """Watch for markdown file changes."""
    
    def __init__(self, processor):
        """Initialize with a document processor."""
        self.processor = processor
        self.watched_extensions = {".md", ".markdown"}
    
    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification events."""
        if not event.is_directory and any(event.src_path.endswith(ext) for ext in self.watched_extensions):
            self.processor.process_file(event.src_path)
    
    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file creation events."""
        if not event.is_directory and any(event.src_path.endswith(ext) for ext in self.watched_extensions):
            self.processor.process_file(event.src_path)


def start_watcher(processor, directory: str = None) -> Observer:
    """Start watching the directory for file changes."""
    if directory is None:
        directory = processor.config.get("vault_dir")
    
    observer = Observer()
    handler = MarkdownWatcher(processor)
    observer.schedule(handler, directory, recursive=True)
    observer.start()
    
    return observer