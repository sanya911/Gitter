import os
import json
import hashlib
import time
from .command import Command
import sys


class CommitCommand(Command):
    def __init__(self, args):
        super().__init__(args)
        self.message = self._parse_commit_message()

    def _parse_commit_message(self):
        """Extracts the commit message from args."""
        if "-m" in self.args:
            msg_index = self.args.index("-m")
            if msg_index + 1 < len(self.args):
                return self.args[msg_index + 1]
            else:
                print("Error: Commit message cannot be empty.")
                sys.exit(1)
        print("Error: Commit message is required.")
        sys.exit(1)

    def execute(self):
        if not os.path.exists(".gitter"):
            print("Error: Gitter repository not initialized. Run 'gitter init'.")
            return

        index_file = ".gitter/index.json"
        commits_file = ".gitter/commits.json"

        try:
            with open(index_file, "r") as f:
                index = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print("Error: No staged files to commit.")
            return

        if not index:
            print("Error: No changes to commit.")
            return

        commit_hash = self._generate_commit_hash(index)

        commit_data = {
            "hash": commit_hash,
            "message": self.message,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "files": index
        }

        # Load existing commits
        if os.path.exists(commits_file):
            with open(commits_file, "r") as f:
                commits = json.load(f)
        else:
            commits = []

        commits.append(commit_data)

        with open(commits_file, "w") as f:
            json.dump(commits, f, indent=4)

        # Clear the index after committing
        with open(index_file, "w") as f:
            json.dump({}, f)

        print(f"Committed with hash: {commit_hash}")

    def _generate_commit_hash(self, index):
        """Generates a unique commit hash including file contents."""
        hasher = hashlib.sha1()
        hasher.update(self.message.encode())
        hasher.update(time.strftime("%Y-%m-%d %H:%M:%S").encode())

        for file, file_hash in sorted(index.items()):
            hasher.update(file.encode())
            hasher.update(file_hash.encode())

        return hasher.hexdigest()
