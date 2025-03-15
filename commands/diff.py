import difflib
import json
import os

from utils import (
    read_committed_file,
    read_file_content,
    get_files,
    hash_file,
    should_ignore,
)
from .command import Command


class DiffCommand(Command):
    def __init__(self, args):
        super().__init__(args)
        # Add option to ignore whitespace changes
        self.ignore_whitespace = "-w" in self.args or "--ignore-whitespace" in self.args
        # Filter out our custom flags
        self.args = [arg for arg in self.args if arg not in ["-w", "--ignore-whitespace"]]
        # Load ignore patterns
        self.ignore_patterns = self.load_ignore_patterns()

    def load_commit_hashes(self):
        """Loads the latest committed file hashes from .gitter/commits.json"""
        commits_file = ".gitter/commits.json"
        if os.path.exists(commits_file):
            try:
                with open(commits_file, "r") as f:
                    commits = json.load(f)
                if commits:
                    return commits[-1]["files"]  # Latest commit file hashes
            except (FileNotFoundError, json.JSONDecodeError):
                pass
        return {}

    def load_index(self):
        """Loads the indexed (staged) file hashes from .gitter/index.json"""
        index_file = ".gitter/index.json"
        if os.path.exists(index_file):
            with open(index_file, "r") as f:
                return json.load(f)
        return {}

    def show_diff(self, file_path, old_content, new_content):
        """Displays the diff output in a Git-style format."""
        # Make sure both old_content and new_content are lists of strings without line endings
        if isinstance(old_content, str):
            old_lines = old_content.splitlines()
        else:
            old_lines = [line.rstrip('\n') if isinstance(line, str) else str(line).rstrip('\n') for line in old_content]

        if isinstance(new_content, str):
            new_lines = new_content.splitlines()
        else:
            new_lines = [line.rstrip('\n') if isinstance(line, str) else str(line).rstrip('\n') for line in new_content]

        # If ignoring whitespace, normalize whitespace in both versions
        if self.ignore_whitespace:
            old_lines = [' '.join(line.split()) for line in old_lines]
            new_lines = [' '.join(line.split()) for line in new_lines]

            # Also remove empty lines if ignoring whitespace
            old_lines = [line for line in old_lines if line.strip()]
            new_lines = [line for line in new_lines if line.strip()]

        # Generate unified diff
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            n=3,  # Show 3 lines of context
            lineterm=""
        ))

        # Only show diff if there are changes
        if diff:
            print(f"\ndiff --git a/{file_path} b/{file_path}")
            # Print each line of the diff
            for line in diff:
                print(line)
            return True
        return False

    def execute(self):
        if not os.path.exists(".gitter"):
            print("Error: Gitter repository not initialized. Run 'gitter init'.")
            return

        committed_hashes = self.load_commit_hashes()  # Last committed state
        index_hashes = self.load_index()  # Staged files
        changes_found = False

        if self.args:
            valid_files, _ = get_files(self.args, self.ignore_patterns)
        else:
            # Get all existing files in the working directory
            all_files, _ = get_files(["."], self.ignore_patterns)
            # Combine with files that might be in commits but removed from filesystem
            valid_files = set(all_files) | set(committed_hashes.keys()) | set(index_hashes.keys())
            # Filter out ignored files from valid_files
            valid_files = [f for f in valid_files if not should_ignore(f, self.ignore_patterns)]

        for file_path in valid_files:
            # Skip ignored files
            if should_ignore(file_path, self.ignore_patterns):
                continue

            current_hash = hash_file(file_path)

            # Case 1: File exists in commits, check for modifications
            if file_path in committed_hashes:
                committed_hash = committed_hashes[file_path]

                # File deleted from working directory
                if not current_hash and os.path.exists(file_path) is False:
                    old_content = read_committed_file(committed_hash)
                    # Use difflib for deleted files too
                    if self.show_diff(file_path, old_content, []):
                        changes_found = True

                # File modified
                elif current_hash and current_hash != committed_hash:
                    old_content = read_committed_file(committed_hash)
                    new_content = read_file_content(file_path)
                    if self.show_diff(file_path, old_content, new_content):
                        changes_found = True

            # Case 2: New file not in commits
            elif os.path.exists(file_path) and file_path not in committed_hashes:
                new_content = read_file_content(file_path)
                # Use difflib for new files too
                if new_content and self.show_diff(file_path, [], new_content):
                    changes_found = True

        if not changes_found:
            print("No differences found.")
