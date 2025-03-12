class CommandFactory:
    @staticmethod
    def get_command(command_name):
        # commands = {
        #     "init": init.run,
        #     "add": add.run,
        #     "status": status.run,
        #     "commit": commit.run,
        #     "log": log.run,
        #     "diff": diff.run,
        #     "help": helping.run,
        #     "rebase": rebase.run,
        #
        # }
        commands = {"abc": "def"}
        return commands.get(command_name, None)