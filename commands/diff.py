import difflib
import json
import os

from utils import read_committed_file, read_file_content, get_files, hash_file
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
        """Displays the diff output in a Git-style format"""
        # Ensure content is string before using splitlines()
        if isinstance(old_content, list):
            old_content = "\n".join(old_content)
        if isinstance(new_content, list):
            new_content = "\n".join(new_content)

        old_lines = old_content.splitlines() if old_content else []
        new_lines = new_content.splitlines() if new_content else []

        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            lineterm="",
        )
        diff_output = "\n".join(diff)

        if diff_output:
            print(diff_output)

    def execute(self):
        if not os.path.exists(".gitter"):
            print("Error: Gitter repository not initialized. Run 'gitter init'.")
            return

        committed_hashes = self.load_commit_hashes()  # Last committed state
        index_hashes = self.load_index()  # Staged files
        modified_files = []

        # If specific files or directories are given, filter accordingly
        if self.args:
            valid_files, _ = get_files(self.args)
        else:
            # Get only modified files instead of all files
            valid_files = set(committed_hashes.keys()) | set(index_hashes.keys())

        for file_path in valid_files:
            current_hash = hash_file(file_path)

            if file_path in committed_hashes:
                committed_hash = committed_hashes[file_path]
                if current_hash and current_hash != committed_hash:
                    old_content = read_committed_file(file_path)
                    new_content = read_file_content(file_path)
                    modified_files.append(file_path)
                    self.show_diff(file_path, old_content, new_content)

            elif file_path not in committed_hashes and file_path not in index_hashes:
                # New untracked file (show as added content)
                new_content = read_file_content(file_path)
                if isinstance(new_content, list):
                    new_content = "\n".join(new_content)

                print(f"--- a/{file_path}")
                print(f"+++ b/{file_path}")
                for line in new_content.splitlines():
                    print(f"+{line}")  # New file, so everything is an addition

        if not modified_files:
            print("No differences found.")
