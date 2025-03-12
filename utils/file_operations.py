import glob
import hashlib
import os


def get_files(args):
    """Returns a tuple of (valid_files, missing_files) matching the given arguments, including subdirectories."""
    if not args:
        print("Error: No files specified.")
        return [], []

    valid_files = []
    missing_files = []

    for arg in args:
        if arg == ".":
            for root, _, files in os.walk(os.getcwd()):
                for file in files:
                    valid_files.append(os.path.join(root, file))
        elif "*" in arg:
            matched_files = glob.glob(arg, recursive=True)
            if matched_files:
                valid_files.extend([f for f in matched_files if os.path.isfile(f)])
            else:
                missing_files.append(arg)
        elif os.path.isfile(arg):
            valid_files.append(arg)
        else:
            missing_files.append(arg)

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


def read_committed_file(file_path):
    """Reads the committed version of a file from the .gitter/objects directory."""
    committed_path = f".gitter/objects/{file_path.replace('/', '_')}"
    return read_file_content(committed_path)


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
