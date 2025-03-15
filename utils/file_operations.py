import glob
import hashlib
import os
import fnmatch


def get_files(paths, ignore_patterns=None):
    """
    Get valid files from a list of paths, filtering out ignored files.

    Args:
        paths (list): List of file paths or directories to check.
        ignore_patterns (list): List of glob patterns to ignore.

    Returns:
        tuple: (valid_files, missing_files)
    """
    valid_files = []
    missing_files = []

    for path in paths:
        if os.path.isdir(path):
            # If it's a directory, recursively add all files
            for root, _, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if not should_ignore(file_path, ignore_patterns):
                        valid_files.append(file_path)
        elif os.path.exists(path):
            # If it's a file, add it if not ignored
            if not should_ignore(path, ignore_patterns):
                valid_files.append(path)
        else:
            # Handle glob patterns
            import glob
            glob_files = glob.glob(path)
            if glob_files:
                for file in glob_files:
                    if os.path.isfile(file) and not should_ignore(file, ignore_patterns):
                        valid_files.append(file)
            else:
                missing_files.append(path)

    return valid_files, missing_files


def hash_file(path):
    """Returns the SHA-1 hash of the given file."""
    try:
        hasher = hashlib.sha1()
        with open(path, "rb") as f:
            hasher.update(f.read())
        return hasher.hexdigest()
    except Exception as e:
        print(f"Error processing file {path}: {str(e)}")
        return None


def read_file_content(file_path):
    """Reads the content of a file and returns it as a list of lines. Handles both text and binary files."""
    try:
        with open(file_path, "rb") as f:
            content = f.read()
            try:
                return content.decode("utf-8").splitlines(True)  # Try decoding as UTF-8
            except UnicodeDecodeError:
                return ["[BINARY FILE - CANNOT DISPLAY CONTENT]\n"]  # Mark as binary
    except FileNotFoundError:
        return []


def read_committed_file(file_hash):
    """Reads the committed version of a file from the .gitter/objects directory using its hash."""
    object_path = f".gitter/objects/{file_hash[:2]}/{file_hash[2:]}"

    if os.path.exists(object_path):
        with open(object_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.readlines()  # Return as list of lines for diff processing
    return []



def write_committed_file(file_path, content):
    """Stores the committed version of a file in .gitter/objects."""
    os.makedirs(".gitter/objects", exist_ok=True)
    committed_path = f".gitter/objects/{file_path.replace('/', '_')}"
    with open(committed_path, "wb") as f:
        if isinstance(content, str):
            f.write(content.encode("utf-8"))  # Encode as UTF-8
        elif isinstance(content, list):
            f.writelines(
                [line.encode("utf-8", "ignore") for line in content]
            )  # Write line by line
        else:
            f.write(content)  # Handle raw binary data


import fnmatch

def should_ignore(file_path, ignore_patterns=None):
    """
    Check if a file should be ignored based on the provided patterns.

    Args:
        file_path (str): The path to the file to check.
        ignore_patterns (list): List of glob patterns to ignore. If None, uses default patterns.

    Returns:
        bool: True if the file should be ignored, False otherwise.
    """
    # Default ignore patterns
    default_patterns = [
        "*.pyc", "*.pyo", "*.pyd",
        ".gitter/*", "__pycache__/*",
        "*.so", "*.o", "*.a", "*.dll",
        ".git/**", ".git/*", ".git"  # FULLY ignore .git/ directories and all subfiles
    ]

    patterns = ignore_patterns or default_patterns

    # **Check for exact directory match**
    if file_path in [".git", ".gitter"]:
        return True

    # **Check if the path starts with an ignored directory**
    for pattern in patterns:
        if pattern.endswith("/*") or pattern.endswith("/**"):
            base_dir = pattern.rstrip("/*")
            if file_path.startswith(base_dir):
                return True  # Ignore everything inside

        # Check file-level ignore
        file_name = os.path.basename(file_path)
        if fnmatch.fnmatch(file_name, pattern) or fnmatch.fnmatch(file_path, pattern):
            return True

    return False

