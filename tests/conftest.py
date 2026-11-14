"""Shared pytest fixtures.

Tests that need Spark take the `spark` fixture. Only those tests connect to
Databricks serverless; all other tests stay fast and run offline.
"""

import os

import pytest
from databricks.connect import DatabricksSession
from pyspark.sql import SparkSession


@pytest.fixture(scope="session")
def spark() -> SparkSession:
    """One Databricks Connect session on serverless compute, shared by all tests.

    Locally this uses the `nba` CLI profile (OAuth). In CI, credentials come from
    the DATABRICKS_HOST / DATABRICKS_TOKEN environment variables instead.
    """
    builder = DatabricksSession.builder.serverless(True)
    if "DATABRICKS_HOST" not in os.environ:
        builder = builder.profile(os.environ.get("DATABRICKS_CONFIG_PROFILE", "nba"))
    return builder.getOrCreate()
