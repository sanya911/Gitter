import difflib
import json
import os

from utils import (get_files, hash_file, read_committed_file,
                   read_file_content, should_ignore)

from .command import Command


class DiffCommand(Command):
    def __init__(self, args):
        super().__init__(args)
        # Add option to ignore whitespace changes
        self.ignore_whitespace = "-w" in self.args or "--ignore-whitespace" in self.args
        # Filter out our custom flags
        self.args = [
            arg for arg in self.args if arg not in ["-w", "--ignore-whitespace"]
        ]
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
            old_lines = [
                line.rstrip("\n") if isinstance(line, str) else str(line).rstrip("\n")
                for line in old_content
            ]

        if isinstance(new_content, str):
            new_lines = new_content.splitlines()
        else:
            new_lines = [
                line.rstrip("\n") if isinstance(line, str) else str(line).rstrip("\n")
                for line in new_content
            ]

        # If ignoring whitespace, normalize whitespace in both versions
        if self.ignore_whitespace:
            old_lines = [" ".join(line.split()) for line in old_lines]
            new_lines = [" ".join(line.split()) for line in new_lines]

            # Also remove empty lines if ignoring whitespace
            old_lines = [line for line in old_lines if line.strip()]
            new_lines = [line for line in new_lines if line.strip()]

        # Check if files are identical
        if old_lines == new_lines:
            return False

        # Generate unified diff
        diff = list(
            difflib.unified_diff(
                old_lines,
                new_lines,
                fromfile=f"a/{file_path}",
                tofile=f"b/{file_path}",
                n=3,  # Show 3 lines of context
                lineterm="",
            )
        )

        # Only show diff if there are changes
        if diff:
            print(f"diff --git a/{file_path} b/{file_path}")
            # Print only the modified chunks, skipping unnecessary empty lines
            for line in diff:
                if (
                    line.strip()
                    or line.startswith("+")
                    or line.startswith("-")
                    or line.startswith("@")
                ):
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
            valid_files = (
                set(all_files) | set(committed_hashes.keys()) | set(index_hashes.keys())
            )
            # Filter out ignored files from valid_files
            valid_files = [
                f for f in valid_files if not should_ignore(f, self.ignore_patterns)
            ]

        for file_path in valid_files:
            # Skip ignored files
            if should_ignore(file_path, self.ignore_patterns):
                continue

            # Skip files that are not in the commit history
            if file_path not in committed_hashes:
                continue

            current_hash = hash_file(file_path)
            committed_hash = committed_hashes[file_path]

            # File deleted from working directory
            if not current_hash and os.path.exists(file_path) is False:
                old_content = read_committed_file(committed_hash)
                print(f"diff --git a/{file_path} b/{file_path}")
                print(f"--- a/{file_path}")
                print(f"+++ /dev/null")
                # Only print non-empty lines
                for line in old_content:
                    if isinstance(line, str) and line.strip():
                        print(f"-{line.rstrip()}")
                changes_found = True

            # File exists and has been modified
            elif current_hash and current_hash != committed_hash:
                old_content = read_committed_file(committed_hash)
                new_content = read_file_content(file_path)
                if self.show_diff(file_path, old_content, new_content):
                    changes_found = True

        if not changes_found:
            print("No differences found.")
