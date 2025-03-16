from commands import (AddCommand, CommitCommand, DiffCommand, HelpCommand,
                      InitCommand, LogCommand, StatusCommand)


class CommandFactory:
    @staticmethod
    def get_command(command_name):
        commands = {
            "init": InitCommand,
            "add": AddCommand,
            "status": StatusCommand,
            "commit": CommitCommand,
            "log": LogCommand,
            "diff": DiffCommand,
            "help": HelpCommand,
        }
        return commands.get(command_name, None)
