import os
import hashlib
import glob


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
