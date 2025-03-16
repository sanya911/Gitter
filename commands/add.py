import json
import os

from utils import get_files, hash_file

from .command import Command


class AddCommand(Command):
    def __init__(self, args):
        super().__init__(args)
        # Load ignore patterns
        self.ignore_patterns = self.load_ignore_patterns()

    def execute(self):
        if not os.path.exists(".gitter"):
            print("Gitter repository not initialized.\nRun 'gitter init'.")
            return

        if not self.args:
            print("Error: No files specified for adding.")
            return

        # Load existing index
        index_file = ".gitter/index.json"
        if os.path.exists(index_file):
            with open(index_file, "r") as f:
                index = json.load(f)
        else:
            index = {}

        valid_files, missing_files = get_files(self.args, self.ignore_patterns)
        if not valid_files:
            print(
                f"Error: No valid files found to add. Named as {', '.join(self.args)}"
            )
            return

        newly_staged = []
        for file in valid_files:
            file_hash = hash_file(file)
            if file_hash:
                # Skip files that are already staged and unchanged
                if file in index and index[file] == file_hash:
                    continue
                index[file] = file_hash
                newly_staged.append(file)

        # Update the index only if there are new or modified files
        if newly_staged:
            with open(index_file, "w") as f:
                json.dump(index, f, indent=4)
            print("Files successfully added to index:", ", ".join(newly_staged))
        else:
            print("No new changes detected. Nothing to add.")

        # Warn about missing files
        if missing_files:
            print(
                f"Warning: The following files could not be added as they were not found: {', '.join(missing_files)}"
            )
