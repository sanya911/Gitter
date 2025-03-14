import hashlib
import json
import os
import sys
import time

from utils import get_files, hash_file, read_file_content, write_committed_file
from .command import Command


class CommitCommand(Command):
    def __init__(self, args):
        super().__init__(args)
        self.args = self._split_combined_flags(self.args)  # NEW: Split combined flags like `-am`
        self.auto_stage = "-a" in self.args
        self.message = self._parse_commit_message()

    def _split_combined_flags(self, args):
        """Splits combined flags like '-am' into ['-a', '-m']."""
        split_args = []
        for arg in args:
            if arg.startswith("-") and len(arg) > 2:  # Detect combined flags
                split_args.extend([f"-{char}" for char in arg[1:]])  # Split each flag
            else:
                split_args.append(arg)
        return split_args

    def _parse_commit_message(self):
        """Extracts the commit message from args, supporting multiple -m messages."""
        messages = []
        i = 0
        while i < len(self.args):
            if self.args[i] == "-m":
                if i + 1 < len(self.args):
                    messages.append(self.args[i + 1])
                    i += 1  # Skip next since it's the message
                else:
                    print("Error: Commit message cannot be empty.")
                    sys.exit(1)
            i += 1

        if not messages:
            print("Error: Commit message is required.")
            sys.exit(1)

        return "\n".join(messages)

    def load_index(self):
        """Loads the indexed file hashes from .gitter/index.json"""
        index_file = ".gitter/index.json"
        if os.path.exists(index_file):
            with open(index_file, "r") as f:
                return json.load(f)
        return {}

    def load_commits(self):
        """Loads existing commits from .gitter/commits.json"""
        commits_file = ".gitter/commits.json"
        if os.path.exists(commits_file):
            with open(commits_file, "r") as f:
                return json.load(f)
        return []

    def save_commit(self, index):
        """Saves the commit metadata and stores committed file versions."""
        commits = self.load_commits()
        commit_hash = self._generate_commit_hash(index)

        commit_data = {
            "hash": commit_hash,
            "message": self.message,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "files": index,
        }
        commits.append(commit_data)

        with open(".gitter/commits.json", "w") as f:
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

        if self.auto_stage:
            # Auto-stage all modified & deleted files before commit
            all_files, _ = get_files(["."])
            for file in all_files:
                file_hash = hash_file(file)
                if file_hash:
                    index[file] = file_hash

        if not index:
            print("No changes to commit.")
            return

        self.save_commit(index)

        # Keep staged files in index, only remove committed ones
        with open(".gitter/index.json", "w") as f:
            json.dump({}, f)

        print("Committed successfully.")
