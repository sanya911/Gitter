import json
import os
import hashlib

from utils import hash_file, should_ignore

from .command import Command






class StatusCommand(Command):
    # jhgv
    def __init__(self, args):
        super().__init__(args)
        # Load ignore patterns
        self.ignore_patterns = self.load_ignore_patterns()

    def get_current_file_hashes(self):
        """Generates the latest hash values for all files in the repository."""
        file_hashes = {}

        # Use consistent path handling
        for root, _, files in os.walk("."):
            for file in files:
                # Create path and normalize to avoid ./ prefix issues
                file_path = os.path.normpath(os.path.join(root, file))

                # Skip ignored files
                if should_ignore(file_path, self.ignore_patterns):
                    continue

                file_hash = hash_file(file_path)
                if file_hash:
                    # Store without ./ prefix for consistency
                    if file_path.startswith("./"):
                        file_path = file_path[2:]
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
                    commit_files = commits[-1]["files"]
                    # Normalize paths from commit for consistency
                    normalized_files = {}
                    for path, hash_val in commit_files.items():
                        norm_path = os.path.normpath(path)
                        if norm_path.startswith("./"):
                            norm_path = norm_path[2:]
                        normalized_files[norm_path] = hash_val
                    return normalized_files
            except Exception as e:
                print(f"Error loading commits: {e}")
        return {}

    def load_index_hashes(self):
        """Loads the index file hashes (staged files)."""
        index_file = ".gitter/index.json"
        if os.path.exists(index_file):
            try:
                with open(index_file, "r") as f:
                    index_files = json.load(f)
                    # Normalize paths from index for consistency
                    normalized_files = {}
                    for path, hash_val in index_files.items():
                        norm_path = os.path.normpath(path)
                        if norm_path.startswith("./"):
                            norm_path = norm_path[2:]
                        normalized_files[norm_path] = hash_val
                    return normalized_files
            except Exception as e:
                print(f"Error loading index: {e}")
        return {}

    def execute(self):
        if not os.path.exists(".gitter"):
            print("Error: Gitter repository not initialized. Run 'gitter init'.")
            return

        # Load all file hashes with consistent path formatting
        last_commit_hashes = self.load_last_commit_hashes()
        index_hashes = self.load_index_hashes()
        current_hashes = self.get_current_file_hashes()

        # Calculate file statuses
        staged_files = []
        unstaged_files = []
        untracked_files = []

        # Check all files from all sources
        all_files = set(current_hashes.keys()) | set(index_hashes.keys()) | set(last_commit_hashes.keys())

        for file in sorted(all_files):
            if should_ignore(file, self.ignore_patterns):
                continue

            # Check file status across all locations
            in_commit = file in last_commit_hashes
            in_index = file in index_hashes
            in_working = file in current_hashes

            # File is in index (staged)
            if in_index:
                if not in_commit or index_hashes[file] != last_commit_hashes.get(file, ""):
                    staged_files.append(file)

            # File is in last commit and working directory (potential unstaged changes)
            if in_commit and in_working:
                if current_hashes[file] != last_commit_hashes[file]:
                    if not in_index or current_hashes[file] != index_hashes.get(file, ""):
                        unstaged_files.append(file)

            # File is only in working directory (untracked)
            if in_working and not in_commit and not in_index:
                untracked_files.append(file)

            # File is in commit but not in working directory (deleted)
            if in_commit and not in_working and not in_index:
                unstaged_files.append(file + " (deleted)")

        # Display results
        if staged_files:
            print("Changes to be committed:")
            for file in staged_files:
                print(f"    modified: {file}")
            print()

        if unstaged_files:
            print("Changes not staged for commit:")
            for file in unstaged_files:
                if " (deleted)" in file:
                    base_name = file.replace(" (deleted)", "")
                    print(f"    deleted:  {base_name}")
                else:
                    print(f"    modified: {file}")
            print()

        if untracked_files:
            print("Untracked files:")
            for file in untracked_files:
                print(f"    {file}")
            print()

        if not (staged_files or unstaged_files or untracked_files):
            print("No changes detected.")