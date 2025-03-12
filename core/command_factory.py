from commands import InitCommand, AddCommand, StatusCommand, CommitCommand, DiffCommand, LogCommand


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
            # "help": helping.run,
        }
        return commands.get(command_name, None)