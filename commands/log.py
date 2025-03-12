import os
import json
from .command import Command


class LogCommand(Command):
    def __init__(self, args):
        super().__init__(args)

    def execute(self):
        if not os.path.exists(".gitter"):
            print("Error: Gitter repository not initialized. Run 'gitter init'.")
            return

        commits_file = ".gitter/commits.json"
        if not os.path.exists(commits_file):
            print("No commits found.")
            return

        try:
            with open(commits_file, "r") as f:
                commits = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print("Error: Commit log is corrupted.")
            return

        for commit in reversed(commits):
            print(f"commit {commit['hash']}")
            print(f"Author: user")
            print(f"Date: {commit['timestamp']}")
            print(f"\n  {commit['message']}\n")