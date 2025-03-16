import hashlib
import json
import os
import sys
import time

from utils import get_files, hash_file, read_file_content, should_ignore

from .command import Command


class CommitCommand(Command):
    def __init__(self, args):
        super().__init__(args)
        self.args = self._split_combined_flags(self.args)  # Ensure -am works
        self.auto_stage = "-a" in self.args
        self.message = self._parse_commit_message()
        # Load ignore patterns
        self.ignore_patterns = self.load_ignore_patterns()

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
        """Saves the commit metadata and stores committed file versions in a Git-like object store."""
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

        # Store committed file contents in .gitter/objects using SHA-1 hash filenames
        for file_path, file_hash in index.items():
            file_content = read_file_content(file_path)

            # Convert list to string before writing
            if isinstance(file_content, list):
                file_content = "\n".join(file_content)

            self.store_object(file_hash, file_content)

    def store_object(self, file_hash, content):
        """Stores file content in a Git-like object format (.gitter/objects/<hash-prefix>/<hash>)"""
        object_dir = f".gitter/objects/{file_hash[:2]}"  # First 2 chars as folder
        object_path = f"{object_dir}/{file_hash[2:]}"

        os.makedirs(object_dir, exist_ok=True)

        with open(object_path, "w") as f:
            f.write(content)  # Fix: Ensure content is always a string

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
            all_files, _ = get_files(["."], self.ignore_patterns)
            for file in all_files:
                if not should_ignore(file, self.ignore_patterns):
                    file_hash = hash_file(file)
                    if file_hash:
                        index[file] = file_hash

        if not index:
            print("No changes to commit.")
            return

        self.save_commit(index)

        # Clear index after commit
        with open(".gitter/index.json", "w") as f:
            json.dump({}, f)

        print(f"Committed successfully with hash: {self._generate_commit_hash(index)}")
