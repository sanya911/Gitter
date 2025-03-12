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

        for file, hash_value in current_hashes.items():
            if file in index:
                if index[file] != hash_value:
                    unstaged_files.append(file)
                else:
                    untracked_files.append(file)

        for file in index:
            if file in current_hashes and index[file] == current_hashes[file]:
                staged_files.append(file)
            elif file not in current_hashes:
                print(f"Warning: {file} was staged but is now missing.")

        untracked_files = [file for file in untracked_files if file not in staged_files]

        if staged_files:
            print("Changes to be commited:")
            for file in staged_files:
                print(f"    modified: {file}")

        if unstaged_files:
            print("Changes not staged for commit:")
            for file in unstaged_files:
                print(f"    modified: {file}")

        if untracked_files:
            print("Untracked files:")
            for file in untracked_files:
                print(f"    modified: {file}")

        if not (staged_files or unstaged_files or untracked_files):
            print("No changes detected.")