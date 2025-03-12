from .command import Command
import os
from utils import hash_file
import json
import time
import hashlib


class CommitCommand(Command):
    def __init__(self, args):
        super().__init__(args)
        self.message = self._parse_commit_message()
        self.auto_add = "-a" in args
        self.index = {}

    def _parse_commit_message(self):
        """Extracts the commit message from args."""
        message_parts = []
        if "-m" in self.args:
            msg_index = self.args.index("-m")
            if msg_index + 1 < len(self.args):
                message_parts.append(self.args[msg_index + 1])
            else:
                print("Error: Commit message cannot be empty.")
                exit(1)
        return "\n".join(message_parts)

    def execute(self):
        if not os.path.exists(".gitter"):
            print("Error: Gitter repository not initialized. Run 'gitter init'.")
            return

        with open(".gitter/index.json", "r") as f:
            self.index = json.load(f)

        if self.auto_add:
            self._add_unstaged_files()

        if not self.index:
            print("Error: No changes to commit.")
            return

        commit_hash = self._generate_commit_hash()
        commit_data = {
            "hash": commit_hash,
            "message": self.message,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "files": self.index
        }

        with open(".gitter/commits.json", "r") as f:
            commits = json.load(f)
        commits.append(commit_data)

        with open(".gitter/commits.json", "w") as f:
            json.dump(commits, f, indent=4)

        with open(".gitter/index.json", "w") as f:
            json.dump({}, f)  # Clear index after commit

        print(f"Committed with hash: {commit_hash}")

    def _generate_commit_hash(self):
        """Generates a unique commit hash."""
        commit_string = self.message + time.strftime("%Y-%m-%d %H:%M:%S")
        return hashlib.sha1(commit_string.encode()).hexdigest()

    def _add_unstaged_files(self):
        """Automatically stages all modified files if `-a` is used."""
        for root, _, files in os.walk(os.getcwd()):
            for file in files:
                file_path = os.path.join(root, file)
                file_hash = hash_file(file_path)
                if file_hash:
                    self.index[file_path] = file_hash
