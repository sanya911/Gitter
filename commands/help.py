import sys
from .command import Command


class HelpCommand(Command):

    COMMANDS = {
        "init": "Create an empty Gitter repository",
        "add": "Add file contents to the index",
        "status": "Show the working tree status",
        "commit": "Record changes to the repository",
        "log": "Show commit logs",
        "diff": "Show changes between commits, commit and working tree",
        "help": "Display help information",
    }

    COMMAND_DETAILS = {
        "init": """
    NAME:
        init - Create an empty Gitter repository
    SYNOPSIS:
        gitter init
    DESCRIPTION:
        Initializes a new Gitter repository in the current directory.
            """,
        "add": """
    NAME:
        add - Add file contents to the index
    SYNOPSIS:
        gitter add <file>
        gitter add .
    DESCRIPTION:
        Adds file contents to the index for tracking. Use '.' to add all modified files.
            """,
        "status": """
    NAME:
        status - Show the working tree status
    SYNOPSIS:
        gitter status
    DESCRIPTION:
        Displays which files are staged for commit, unstaged changes, and untracked files.
            """,
        "commit": """
    NAME:
        commit - Record changes to the repository
    SYNOPSIS:
        gitter commit -m [-a ] <msg>
    DESCRIPTION:
        Create a new commit containing the current contents of the index and the given log message.
    OPTIONS:
        -a: Automatically stage files that have been modified and deleted.
        -m: Use the given <msg> as the commit message. If multiple -m options are given, their values are concatenated.
            """,
        "log": """
    NAME:
        log - Show commit logs
    SYNOPSIS:
        gitter log
    DESCRIPTION:
        Displays the commit history in reverse chronological order.
            """,
        "diff": """
    NAME:
        diff - Show changes between commits, commit and working tree
    SYNOPSIS:
        gitter diff
        gitter diff <file>
        gitter diff <directory>
    DESCRIPTION:
        Displays differences between the working directory and the last committed version.
            """,
    }

    def execute(self):
        if len(self.args) == 0:
            print("These are common Gitter commands:")
            for cmd, desc in self.COMMANDS.items():
                print(f"  {cmd:10} {desc}")
        elif self.args[0] in self.COMMAND_DETAILS:
            print(self.COMMAND_DETAILS[self.args[0]])
        else:
            print(f"Unknown command '{self.args[0]}'. Run 'gitter help' for a list of commands.")
