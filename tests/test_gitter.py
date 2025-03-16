import os
import json
import tempfile
import unittest
import shutil
import subprocess
import sys
from pathlib import Path


class GitterTestCase(unittest.TestCase):
    """Base test case with setup and teardown for testing Gitter commands"""

    def setUp(self):
        """Create a temporary directory for testing"""
        self.test_dir = tempfile.mkdtemp()
        self.old_dir = os.getcwd()
        os.chdir(self.test_dir)

        # Ensure no .gitter directory exists at the start
        if os.path.exists(".gitter"):
            shutil.rmtree(".gitter")

        # Create test files
        with open("test_file1.txt", "w") as f:
            f.write("Test content 1")
        with open("test_file2.txt", "w") as f:
            f.write("Test content 2")

        # Create subdirectory with test file
        os.makedirs("subdir")
        with open("subdir/test_file3.txt", "w") as f:
            f.write("Test content 3")

    def tearDown(self):
        """Clean up temp directory after tests"""
        os.chdir(self.old_dir)
        shutil.rmtree(self.test_dir)

    def run_command(self, command):
        """Helper to run gitter commands for testing"""
        # Get the directory of the gitter project - this is the parent directory of wherever the test is running
        gitter_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Construct the path to the service.py file
        service_path = os.path.join(gitter_path, "service.py")

        # Run the command directly from the test directory
        full_command = f"{sys.executable} {service_path} {command}"

        # Run command and capture both stdout and stderr
        result = subprocess.run(full_command, shell=True, capture_output=True, text=True, cwd=self.test_dir)

        # For debugging, print stdout and stderr
        if result.stdout:
            print(f"Command stdout: {result.stdout}")
        if result.stderr:
            print(f"Command stderr: {result.stderr}")

        return result


class TestInitCommand(GitterTestCase):
    """Test the init command"""

    def test_init_creates_repository(self):
        """Test that init creates the repository structure"""
        result = self.run_command("init")

        # Check command output
        self.assertIn("Initialized empty Gitter repository", result.stdout)

        # Check repository structure
        self.assertTrue(os.path.exists(".gitter"))
        self.assertTrue(os.path.exists(".gitter/index.json"))
        self.assertTrue(os.path.exists(".gitter/commits.json"))
        self.assertTrue(os.path.exists(".gitter/HEAD"))

        # Check file contents
        with open(".gitter/index.json", "r") as f:
            self.assertEqual("{}", f.read())

        with open(".gitter/commits.json", "r") as f:
            self.assertEqual("[]", f.read())

        with open(".gitter/HEAD", "r") as f:
            self.assertEqual("ref: refs/heads/main\n", f.read())

    def test_init_already_initialized(self):
        """Test that init warns if repository already exists"""
        # Run init first time
        self.run_command("init")

        # Run init second time
        result = self.run_command("init")
        self.assertIn("Gitter repository already initialized", result.stdout)


class TestAddCommand(GitterTestCase):
    """Test the add command"""

    def setUp(self):
        """Create a temporary directory for testing"""
        super().setUp()

        # Initialize Gitter
        self.run_command("init")

    def test_add_single_file(self):
        """Test adding a single file to index"""
        # Run the add command
        result = self.run_command("add test_file1.txt")

        self.assertIn("Files successfully added to index", result.stdout)
        self.assertIn("test_file1.txt", result.stdout)

        # Check index contents
        with open(".gitter/index.json", "r") as f:
            index = json.load(f)
            self.assertIn("test_file1.txt", index)

    def test_add_all_files(self):
        """Test adding all files with the dot notation"""
        # Run the add command
        result = self.run_command("add .")
        self.assertIn("Files successfully added to index", result.stdout)

        # Check that our test files are in the index
        with open(".gitter/index.json", "r") as f:
            index = json.load(f)
            self.assertIn("test_file1.txt", index)
            self.assertIn("test_file2.txt", index)
            self.assertIn("subdir/test_file3.txt", index)

    def test_add_nonexistent_file(self):
        """Test adding a file that doesn't exist"""
        result = self.run_command("add nonexistent.txt")
        self.assertIn("Error", result.stdout)

    def test_add_no_new_changes(self):
        """Test adding files that are already in the index"""
        # Add files first time
        self.run_command("add test_file1.txt")

        # Try to add the same file again
        result = self.run_command("add test_file1.txt")
        self.assertIn("No new changes detected", result.stdout)

    def test_add_modified_file(self):
        """Test adding a file that was modified after being staged"""
        # Add file initially
        self.run_command("add test_file1.txt")

        # Modify the file
        with open("test_file1.txt", "w") as f:
            f.write("Modified content")

        # Add again
        result = self.run_command("add test_file1.txt")

        self.assertIn("Files successfully added to index", result.stdout)
        self.assertIn("test_file1.txt", result.stdout)


class TestStatusCommand(GitterTestCase):
    """Test the status command"""

    def setUp(self):
        super().setUp()
        self.run_command("init")

    def test_unstaged_changes(self):
        """Test status with unstaged changes"""
        # Create new file after init
        with open("new_file.txt", "w") as f:
            f.write("New content")

        result = self.run_command("status")
        self.assertIn("Untracked files", result.stdout)
        self.assertIn("new_file.txt", result.stdout)

    def test_staged_changes(self):
        """Test status with staged changes"""
        # Add a file
        self.run_command("add test_file1.txt")

        result = self.run_command("status")
        self.assertIn("Changes to be committed", result.stdout)
        self.assertIn("test_file1.txt", result.stdout)

    def test_modified_after_staging(self):
        """Test status for files modified after staging"""
        # Add a file
        self.run_command("add test_file1.txt")

        # Modify it
        with open("test_file1.txt", "w") as f:
            f.write("Modified after staging")

        result = self.run_command("status")
        self.assertIn("Changes to be committed", result.stdout)
        self.assertIn("Changes not staged for commit", result.stdout)
        self.assertIn("test_file1.txt", result.stdout)

    def test_deleted_file(self):
        """Test status for files that were deleted"""
        # Add a file then delete it
        self.run_command("add test_file1.txt")
        self.run_command("commit -m 'Add test_file1.txt'")
        os.remove("test_file1.txt")

        result = self.run_command("status")
        self.assertIn("deleted", result.stdout)
        self.assertIn("test_file1.txt", result.stdout)


class TestCommitCommand(GitterTestCase):
    """Test the commit command"""

    def setUp(self):
        super().setUp()
        self.run_command("init")

    def test_commit_with_message(self):
        """Test committing staged changes with a message"""
        self.run_command("add test_file1.txt")
        result = self.run_command("commit -m 'Initial commit'")

        self.assertIn("Committed successfully", result.stdout)

        # Check commits file
        with open(".gitter/commits.json", "r") as f:
            commits = json.load(f)
            self.assertEqual(1, len(commits))
            self.assertEqual("Initial commit", commits[0]["message"])
            self.assertIn("test_file1.txt", commits[0]["files"])

        # Check that the index was cleared
        with open(".gitter/index.json", "r") as f:
            index = json.load(f)
            self.assertEqual({}, index)

    def test_commit_auto_stage(self):
        """Test committing with auto-staging option"""
        # Create a file and initialize
        self.run_command("add test_file1.txt")
        self.run_command("commit -m 'First commit'")

        # Modify the file
        with open("test_file1.txt", "w") as f:
            f.write("Modified content")

        # Commit with auto-stage
        result = self.run_command("commit -am 'Auto-staged commit'")

        self.assertIn("Committed successfully", result.stdout)

        # Check commits file
        with open(".gitter/commits.json", "r") as f:
            commits = json.load(f)
            self.assertEqual(2, len(commits))
            self.assertEqual("Auto-staged commit", commits[1]["message"])

    def test_commit_multiple_messages(self):
        """Test committing with multiple -m arguments"""
        self.run_command("add test_file1.txt")
        result = self.run_command("commit -m 'First line' -m 'Second line'")

        self.assertIn("Committed successfully", result.stdout)

        # Check commits file
        with open(".gitter/commits.json", "r") as f:
            commits = json.load(f)
            self.assertEqual("First line\nSecond line", commits[0]["message"])

    def test_commit_no_changes(self):
        """Test committing with no changes staged"""
        result = self.run_command("commit -m 'Empty commit'")

        self.assertIn("No changes to commit", result.stdout)

        # Check that no commit was created
        with open(".gitter/commits.json", "r") as f:
            commits = json.load(f)
            self.assertEqual(0, len(commits))


class TestLogCommand(GitterTestCase):
    """Test the log command"""

    def setUp(self):
        super().setUp()
        self.run_command("init")

    def test_empty_log(self):
        """Test log with no commits"""
        result = self.run_command("log")
        self.assertIn("No commits found", result.stdout)

    def test_log_with_commits(self):
        """Test log with multiple commits"""
        # Add and commit first file
        self.run_command("add test_file1.txt")
        self.run_command("commit -m 'First commit'")

        # Add and commit second file
        self.run_command("add test_file2.txt")
        self.run_command("commit -m 'Second commit'")

        result = self.run_command("log")

        # Check that both commits are shown
        self.assertIn("First commit", result.stdout)
        self.assertIn("Second commit", result.stdout)

        # Check that the most recent commit is shown first
        first_commit_pos = result.stdout.find("First commit")
        second_commit_pos = result.stdout.find("Second commit")
        self.assertTrue(second_commit_pos < first_commit_pos)


class TestDiffCommand(GitterTestCase):
    """Test the diff command"""

    def setUp(self):
        super().setUp()
        self.run_command("init")
        self.run_command("add test_file1.txt")
        self.run_command("commit -m 'Initial commit'")

    def test_diff_modified_file(self):
        """Test diff on a modified file"""
        # Modify the file
        with open("test_file1.txt", "w") as f:
            f.write("Modified content")

        result = self.run_command("diff")

        # Check that diff shows the modification
        self.assertIn("diff --git a/test_file1.txt b/test_file1.txt", result.stdout)
        self.assertIn("-Test content 1", result.stdout)
        self.assertIn("+Modified content", result.stdout)

    def test_diff_specific_file(self):
        """Test diff on a specific file"""
        # Modify multiple files
        with open("test_file1.txt", "w") as f:
            f.write("Modified file 1")

        with open("test_file2.txt", "w") as f:
            f.write("Modified file 2")

        # Run diff on just one file
        result = self.run_command("diff test_file1.txt")

        # Check that only the specified file is included
        self.assertIn("diff --git a/test_file1.txt b/test_file1.txt", result.stdout)
        self.assertIn("Modified file 1", result.stdout)
        self.assertNotIn("test_file2.txt", result.stdout)

    def test_diff_no_changes(self):
        """Test diff when there are no changes"""
        result = self.run_command("diff")
        self.assertIn("No differences found", result.stdout)

    def test_diff_ignore_whitespace(self):
        """Test diff with ignore whitespace option"""
        # Create a file with only whitespace changes
        with open("test_file1.txt", "w") as f:
            f.write("Test   content   1")  # Added extra spaces

        # Run diff with whitespace ignored
        result = self.run_command("diff -w")

        # No differences should be found
        self.assertIn("No differences found", result.stdout)


if __name__ == "__main__":
    unittest.main()