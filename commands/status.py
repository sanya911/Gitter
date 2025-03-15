import json
import os

from utils import hash_file, should_ignore

from .command import Command


class StatusCommand(Command):
    def __init__(self, args):
        super().__init__(args)
        # Load ignore patterns
        self.ignore_patterns = self.load_ignore_patterns()

    @staticmethod
    def get_current_file_hashes(ignore_patterns=None):
        """Generates the latest hash values for all files in the repository."""
        file_hashes = {}
        for root, _, files in os.walk(os.getcwd()):
            for file in files:
                file_path = os.path.join(root, file)
                if should_ignore(file_path, ignore_patterns):
                    continue  # Ignore files based on patterns
                file_hash = hash_file(file_path)
                if file_hash:
                    file_hashes[file_path] = file_hash
        return file_hashes

    def load_last_commit_hashes(self):
        """Loads the latest committed file hashes from the last commit."""
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

    def load_index_hashes(self):
        """Loads the index file hashes (staged files)."""
        index_file = ".gitter/index.json"
        if os.path.exists(index_file):
            try:
                with open(index_file, "r") as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                pass
        return {}

    def execute(self):
        if not os.path.exists(".gitter"):
            print("Error: Gitter repository not initialized. Run 'gitter init'.")
            return

        last_commit_hashes = self.load_last_commit_hashes()
        index_hashes = self.load_index_hashes()
        current_hashes = self.get_current_file_hashes(self.ignore_patterns)
        staged_files = []
        unstaged_files = []
        untracked_files = []

        all_files = set()
        for root, _, files in os.walk(os.getcwd()):
            for file in files:
                file_path = os.path.join(root, file)
                if not should_ignore(file_path, self.ignore_patterns):
                    all_files.add(file_path)

        for file in all_files:
            if ".gitter" in file:
                continue  # Ignore internal files
            if file in index_hashes:
                if (
                    file not in last_commit_hashes
                    or index_hashes[file] != last_commit_hashes[file]
                ):
                    staged_files.append(file)
            elif file in last_commit_hashes:
                if last_commit_hashes[file] != current_hashes.get(file, None):
                    unstaged_files.append(file)
            else:
                untracked_files.append(file)

        if staged_files:
            print("Changes to be committed:")
            for file in staged_files:
                print(f"    modified: {file}")

        if unstaged_files:
            print("Changes not staged for commit:")
            for file in unstaged_files:
                print(f"    modified: {file}")

        if untracked_files:
            print("Untracked files:")
            for file in untracked_files:
                print(f"    {file}")

        if not (staged_files or unstaged_files or untracked_files):
            print("No changes detected.")
