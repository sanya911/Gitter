import sys

from core.command_factory import CommandFactory


def main():
    if len(sys.argv) < 2:
        print(
            "See 'gitter --help' for an overview of the system \n Usage: gitter <command> [args]"
        )
        sys.exit(1)
    command = sys.argv[1]
    args = sys.argv[2:]
    command_class = CommandFactory.get_command(command)
    if command_class:
        try:
            command_instance = command_class(args)
            command_instance.execute()
        except Exception as e:
            print(f"Error executing command {command}: {e} \n See 'gitter --help'")
            sys.exit(1)
    else:
        print(
            "gitter: {} is not a gitter command. \n See 'gitter --help'".format(command)
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
