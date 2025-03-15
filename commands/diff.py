import difflib
import json
import os

from utils import (
    read_committed_file,
    read_file_content,
    get_files,
    hash_file,
)
from .command import Command


class DiffCommand(Command):
    def __init__(self, args):
        super().__init__(args)

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
        """Displays the diff output in a Git-style format with only relevant changes."""
        old_lines = old_content.splitlines() if isinstance(old_content, str) else old_content
        new_lines = new_content.splitlines() if isinstance(new_content, str) else new_content

        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            n=2,
            lineterm="",
        ))

        filtered_diff = []
        show_context = False

        for line in diff:
            if line.startswith("@@"):
                show_context = True
                filtered_diff.append(line)
            elif show_context:
                if line.startswith("-") or line.startswith("+"):
                    filtered_diff.append(line)
                elif filtered_diff and not line.strip():
                    filtered_diff.append(line)

        if filtered_diff:
            print("\n".join(filtered_diff))

    def execute(self):
        if not os.path.exists(".gitter"):
            print("Error: Gitter repository not initialized. Run 'gitter init'.")
            return

        committed_hashes = self.load_commit_hashes()  # Last committed state
        index_hashes = self.load_index()  # Staged files
        modified_files = []

        if self.args:
            valid_files, _ = get_files(self.args)
        else:
            valid_files = set(committed_hashes.keys()) | set(index_hashes.keys())

        for file_path in valid_files:
            current_hash = hash_file(file_path)

            if file_path in committed_hashes:
                committed_hash = committed_hashes[file_path]
                if current_hash and current_hash != committed_hash:
                    old_content = read_committed_file(committed_hash)  # Read committed version
                    new_content = read_file_content(file_path)  # Read current version
                    modified_files.append(file_path)
                    self.show_diff(file_path, old_content, new_content)

            elif file_path not in committed_hashes and file_path not in index_hashes:
                new_content = read_file_content(file_path)
                print(f"--- a/{file_path}")
                print(f"+++ b/{file_path}")
                for line in new_content:
                    print(f"+{line.strip()}")  # New file, so everything is an addition

        if not modified_files:
            print("No differences found.khjgf")
