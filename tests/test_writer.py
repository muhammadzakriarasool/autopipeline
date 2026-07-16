"""Tests for the DataHub writer (mutation) layer."""

from autopipeline.writer import DataHubWriter
from autopipeline.context import DatasetContext


class TestDataHubWriter:
    """Test writer instantiation — actual mutations tested against live DataHub."""

    def test_writer_instantiation(self):
        """We test that the writer can be created.
        (Integration tests need live DataHub — see test_integration.py)
        """
        from autopipeline.connector import DataHubConnector
        conn = DataHubConnector(server="http://localhost:8080", token="fake")
        assert conn.writer is not None
        assert isinstance(conn.writer, DataHubWriter)
