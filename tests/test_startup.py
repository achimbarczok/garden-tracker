"""Unit tests for startup error handling (Requirement 2.4)."""
import os
import subprocess
import sys


def test_startup_fails_on_bad_db(tmp_path):
    """Point DB_PATH at a path inside a non-existent directory; assert non-zero exit and German error log."""
    # A path whose parent directory does not exist — SQLite will fail to open it
    bad_path = str(tmp_path / "nonexistent_dir" / "plants.db")

    env = os.environ.copy()
    env["DB_PATH"] = bad_path

    result = subprocess.run(
        [sys.executable, "-c", "import app"],
        env=env,
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    )

    assert result.returncode != 0, (
        f"Expected non-zero exit code, got {result.returncode}. "
        f"stderr: {result.stderr}"
    )
    assert "Datenbankfehler beim Start" in result.stderr, (
        f"Expected German error message in stderr, got: {result.stderr}"
    )
