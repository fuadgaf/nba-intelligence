"""Guards dev/prod parity: local code must run on the same Python as Databricks serverless."""

import sys


def test_python_version_matches_databricks_serverless() -> None:
    assert sys.version_info[:2] == (3, 12), (
        f"Expected Python 3.12 (Databricks serverless), got {sys.version.split()[0]}"
    )
