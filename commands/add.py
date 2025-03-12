import json
import os

from utils import get_files, hash_file

from .command import Command


class AddCommand(Command):
    def execute(self):
        if not os.path.exists(".gitter"):
            print("Gitter repository not initialized.\n Run 'gitter init.")
            return

        if not self.args:
            print("Error: No files specified for adding.")
            return

        with open(".gitter/index.json", "r") as f:
            index = json.load(f)

        valid_files, missing_files = get_files(self.args)

        if not valid_files:
            print(
                f"Error: No valid files found to add. Named as {', '.join(self.args)}"
            )
            return

        for file in valid_files:
            file_hash = hash_file(file)
            if file_hash:
                index[file] = file_hash

        with open(".gitter/index.json", "w") as f:
            json.dump(index, f)

        if missing_files:
            print(
                f"Warning: The following files could not be added as they were not found: {', '.join(missing_files)}"
            )

        print("Files successfully added to index.")
