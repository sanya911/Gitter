from .command import Command
import os
import json
from utils import hash_file


class StatusCommand(Command):

    @staticmethod
    def get_current_file_hashes():
        """Generates the latest hash values for all files in the repository."""
        file_hashes = {}
        for root, _, files in os.walk(os.getcwd()):
            for file in files:
                file_path = os.path.join(root, file)
                file_hash = hash_file(file_path)
                if file_hash:
                    file_hashes[file_path] = file_hash
        return file_hashes

    def execute(self):
        if not os.path.exists(".gitter"):
            print("Error: Gitter repository not initialized. Run 'gitter init'.")
            return

        try:
            with open(".gitter/index.json", "r") as f:
                index = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print("Error: Corrupt or missing index file. Try reinitializing the repository.")
            return

        current_hashes = self.get_current_file_hashes()
        staged_files = []
        unstaged_files = []
        untracked_files = []

        # Find all files in the working directory
        all_files = {os.path.join(root, file) for root, _, files in os.walk(os.getcwd()) for file in files}

        for file in all_files:
            if file in index:
                # If file is tracked but modified, mark as unstaged
                if index[file] != current_hashes.get(file, None):
                    unstaged_files.append(file)
            else:
                # File is untracked
                untracked_files.append(file)

        # Check if any staged files were deleted
        for file in index:
            if file in current_hashes:
                staged_files.append(file)
            else:
                print(f"Warning: {file} was staged but is now missing.")

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
