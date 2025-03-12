from commands import InitCommand, AddCommand, StatusCommand, CommitCommand


class CommandFactory:
    @staticmethod
    def get_command(command_name):
        commands = {
            "init": InitCommand,
            "add": AddCommand,
            "status": StatusCommand,
            "commit": CommitCommand,
            # "log": log.run,
            # "diff": diff.run,
            # "help": helping.run,
            # "rebase": rebase.run,

        }
        return commands.get(command_name, None)