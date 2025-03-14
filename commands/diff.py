import difflib
import json
import os

from utils import read_committed_file, read_file_content, get_files
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

    def show_diff(self, file_path, old_content, new_content):
        """Displays the diff output in a unified format"""
        old_lines = old_content.splitlines() if isinstance(old_content, str) else []
        new_lines = new_content.splitlines() if isinstance(new_content, str) else []

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

        committed_hashes = self.load_commit_hashes()
        modified_files = []

        # If specific files or directories are given, filter accordingly
        if self.args:
            valid_files, _ = get_files(self.args)
        else:
            valid_files = {
                os.path.join(root, file)
                for root, _, files in os.walk(os.getcwd())
                for file in files
            }

        for file_path in valid_files:
            old_content = read_committed_file(file_path) if file_path in committed_hashes else ""
            new_content = read_file_content(file_path)

            # Convert to string if the function returns a list
            if isinstance(old_content, list):
                old_content = "\n".join(old_content)
            if isinstance(new_content, list):
                new_content = "\n".join(new_content)

            if old_content != new_content:
                modified_files.append(file_path)
                self.show_diff(file_path, old_content, new_content)

        if not modified_files:
            print("No differences found.")
