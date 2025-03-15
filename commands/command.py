from abc import ABC, abstractmethod
import os


class Command(ABC):
    def __init__(self, args):
        self.args = args

    @abstractmethod
    def execute(self):
        pass

    def load_ignore_patterns(self):
        """Load ignore patterns from .gitterignore file and add default patterns."""
        ignore_file = ".gitterignore"
        patterns = []

        if os.path.exists(ignore_file):
            with open(ignore_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.append(line)

        # Add default patterns to ignore
        default_patterns = [
            "*.pyc", "*.pyo", "*.pyd",
            ".gitter/*", "__pycache__/*",
            "*.so", "*.o", "*.a", "*.dll",
            ".git/**",  # Ensure all subdirectories inside .git are ignored
        ]
        patterns.extend(default_patterns)

        return patterns