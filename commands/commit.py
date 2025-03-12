import os
import json
import hashlib
import time
from .command import Command
import sys
from utils import write_committed_file, read_file_content


class CommitCommand(Command):
    def __init__(self, args):
        super().__init__(args)
        self.message = self._parse_commit_message()
        self.auto_stage = "-a" in self.args

    def _parse_commit_message(self):
        """Extracts the commit message from args, supporting multiple -m messages."""
        messages = []
        if "-m" in self.args:
            msg_indices = [i for i, x in enumerate(self.args) if x == "-m"]
            for index in msg_indices:
                if index + 1 < len(self.args):
                    messages.append(self.args[index + 1])
                else:
                    print("Error: Commit message cannot be empty.")
                    sys.exit(1)
            return "\n".join(messages)
        print("Error: Commit message is required.")
        sys.exit(1)

    def load_index(self):
        """Loads the indexed file hashes from .gitter/index.json"""
        index_file = ".gitter/index.json"
        if os.path.exists(index_file):
            with open(index_file, "r") as f:
                return json.load(f)
        return {}

    def save_commit(self, index):
        """Saves the commit metadata and stores committed file versions."""
        commits_file = ".gitter/commits.json"
        os.makedirs(".gitter", exist_ok=True)
        if os.path.exists(commits_file):
            with open(commits_file, "r") as f:
                commits = json.load(f)
        else:
            commits = []

        commit_hash = self._generate_commit_hash(index)
        commit_data = {
            "hash": commit_hash,
            "message": self.message,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "files": index
        }
        commits.append(commit_data)

        with open(commits_file, "w") as f:
            json.dump(commits, f, indent=4)

        # Store committed file contents in .gitter/objects
        for file_path in index.keys():
            content = read_file_content(file_path)
            write_committed_file(file_path, content)

    def _generate_commit_hash(self, index):
        """Generates a unique commit hash including file contents."""
        hasher = hashlib.sha1()
        hasher.update(self.message.encode())
        hasher.update(time.strftime("%Y-%m-%d %H:%M:%S").encode())

        for file, file_hash in sorted(index.items()):
            hasher.update(file.encode())
            hasher.update(file_hash.encode())

        return hasher.hexdigest()

    def execute(self):

        if not os.path.exists(".gitter"):
            print("Error: Gitter repository not initialized. Run 'gitter init'.")
            return

        index = self.load_index()
        if not index:
            print("No changes to commit.")
            return

        self.save_commit(index)

        # Clear the index after commit
        with open(".gitter/index.json", "w") as f:
            json.dump({}, f)

        print("Committed successfully.")
