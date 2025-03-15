from abc import ABC, abstractmethod
import os


class Command(ABC):
    def __init__(self, args):
        self.args = args

    @abstractmethod
    def execute(self):
        pass

    def load_ignore_patterns(self):
        """Load ignore patterns from .gitterignore or use defaults."""
        default_patterns = [
            "*.pyc", "*.pyo", "*.pyd",
            "__pycache__/*", "__pycache__/**",
            "*.so", "*.o", "*.a", "*.dll",
            ".git/*", ".git/**", ".git",  # Ignore .git directory completely
            ".gitter/*", ".gitter/**", ".gitter"  # Ignore .gitter directory completely
        ]

        ignore_file = ".gitterignore"
        if os.path.exists(ignore_file):
            with open(ignore_file, "r") as f:
                custom_patterns = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            return custom_patterns + default_patterns

        return default_patterns