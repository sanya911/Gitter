import json
import os

from utils import get_files, hash_file, should_ignore
from .command import Command


class StatusCommand(Command):
    def __init__(self, args):
        super().__init__(args)
        # Load ignore patterns
        self.ignore_patterns = self.load_ignore_patterns()

    def load_index(self):
        """Loads the indexed (staged) file hashes from .gitter/index.json"""
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

    def execute(self):
        if not os.path.exists(".gitter"):
            print("Error: Gitter repository not initialized. Run 'gitter init'.")
            return

        # Get all files in the working directory
        all_files, _ = get_files(["."], self.ignore_patterns)

        # Filter out files that should be ignored
        all_files = [f for f in all_files if not should_ignore(f, self.ignore_patterns)]

        # Get current index and last commit
        index = self.load_index()
        commit_hashes = self.load_commit_hashes()

        # Calculate current file hashes for comparison
        current_hashes = {}
        for file in all_files:
            file_hash = hash_file(file)
            if file_hash:
                current_hashes[file] = file_hash

        # Track different file states
        staged_new = []
        staged_modified = []
        unstaged_modified = []
        unstaged_deleted = []
        untracked = []

        # Check each file in index
        for file, hash_val in index.items():
            # File in index but not on disk (deleted)
            if file not in current_hashes:
                unstaged_deleted.append(file)
            # File in index and modified after staging
            elif current_hashes[file] != hash_val:
                unstaged_modified.append(file)

            # Determine if file is new or modified in index compared to commit
            if file not in commit_hashes:
                staged_new.append(file)
            elif commit_hashes[file] != hash_val:
                staged_modified.append(file)

        # Find untracked files (not in index)
        untracked = [f for f in all_files if f not in index]

        # Display changes to be committed (staged)
        if staged_new or staged_modified:
            print("Changes to be committed:")
            for file in staged_new:
                print(f"    new file: {file}")
            for file in staged_modified:
                print(f"    modified: {file}")
            print()

        # Display changes not staged for commit
        if unstaged_modified or unstaged_deleted:
            print("Changes not staged for commit:")
            for file in unstaged_modified:
                print(f"    modified: {file}")
            for file in unstaged_deleted:
                print(f"    deleted: {file}")
            print()

        # Display untracked files
        if untracked:
            print("Untracked files:")
            for file in untracked:
                print(f"    {file}")
            print()

        # If no changes at all
        if not (staged_new or staged_modified or unstaged_modified or
                unstaged_deleted or untracked):
            print("No changes (working directory clean)")