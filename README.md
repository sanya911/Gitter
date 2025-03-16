# Gitter

Gitter is a lightweight, simplified Git-like version control system implemented in Python. It provides basic version control functionality to track changes in files, create commits, and view differences between versions.

## Features

- Initialize a new repository
- Stage files for commits
- View the status of your working directory
- Create commits with messages
- View commit history
- Show file differences between commits and working directory

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/gitter.git
cd gitter
```

## Usage

### Basic Commands

```bash
# Initialize a new repository
python service.py init

# Add files to the staging area
python service.py add <file>
python service.py add .  # Add all files

# Check status
python service.py status

# Commit changes
python service.py commit -m "Your commit message"
python service.py commit -am "Auto-stage and commit"  # Auto-stage modified files

# View commit history
python service.py log

# Show differences
python service.py diff
python service.py diff <file>
```

### Command Details

- **init**: Create an empty Gitter repository
- **add**: Stage file contents for the next commit
- **status**: Show the working tree status (staged, unstaged, and untracked files)
- **commit**: Record changes to the repository
  - `-m`: Specify a commit message
  - `-a`: Auto-stage all modified files before committing
- **log**: Show commit history
- **diff**: Show changes between working directory and last commit
  - `-w`: Ignore whitespace changes

## Project Structure

```
.
├── core/
│   ├── command_factory.py
│   └── commands/
│       ├── add.py
│       ├── command.py
│       ├── commit.py
│       ├── diff.py
│       ├── help.py
│       ├── init.py
│       ├── log.py
│       └── status.py
├── utils/
│   └── file_operations.py
├── service.py
├── tests/
│   └── test_gitter.py
└── README.md
```

## Running Tests

To run the test suite:

```bash
python -m unittest tests/test_gitter.py
```

For specific test cases:

```bash
python -m unittest tests.test_gitter.TestInitCommand
python -m unittest tests.test_gitter.TestAddCommand
```

## Development

Gitter uses a command pattern architecture:

1. `service.py` is the entry point
2. `command_factory.py` routes commands to their implementation classes
3. Individual command classes in the `commands` directory handle specific functionality

To add a new command:
1. Create a new command class in the `commands` directory
2. Register the command in `CommandFactory` 
3. Implement tests in `test_gitter.py`