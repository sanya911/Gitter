import os
import json
import difflib
from .command import Command
from utils import read_file_content, read_committed_file


class DiffCommand(Command):
    def __init__(self, args):
        super().__init__(args)

    def load_index(self):
        """Loads the indexed file hashes from .gitter/index.json"""
        index_file = ".gitter/index.json"
        if os.path.exists(index_file):
            with open(index_file, "r") as f:
                return json.load(f)
        return {}

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
        diff = difflib.unified_diff(old_content, new_content,
                                    fromfile=f"a/{file_path}",
                                    tofile=f"b/{file_path}",
                                    lineterm="")
        print("\n".join(diff))

    def execute(self):
        if not os.path.exists(".gitter"):
            print("Error: Gitter repository not initialized. Run 'gitter init'.")
            return

        index = self.load_index()
        committed_hashes = self.load_commit_hashes()
        modified_files = []
        all_files = {os.path.join(root, file) for root, _, files in os.walk(os.getcwd()) for file in files}

        for file_path in all_files:
            if file_path in committed_hashes:
                old_content = read_committed_file(file_path)  # Read committed version
                new_content = read_file_content(file_path)    # Read current working version
                if old_content != new_content:
                    modified_files.append(file_path)
                    self.show_diff(file_path, old_content, new_content)

        if not modified_files:
            print("No differences found.")