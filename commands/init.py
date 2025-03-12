import os

from .command import Command


class InitCommand(Command):
    def execute(self):
        if os.path.exists(".gitter"):
            print("Gitter repository already initialized.")
        else:
            os.makedirs(".gitter")
            with open(".gitter/index.json", "w") as f:
                f.write("{}")
            with open(".gitter/commits.json", "w") as f:
                f.write("[]")
            with open(".gitter/HEAD", "w") as f:
                f.write("ref: refs/heads/main\n")
            print(f"Initialized empty Gitter repository in {os.getcwd()}/.gitter/")
