"""DataHub connector — wraps SDK for metadata queries and mutations."""

from dataclasses import dataclass
from typing import Optional

from datahub.sdk.main_client import DataHubClient

from autopipeline.context import ContextCollector
from autopipeline.writer import DataHubWriter


@dataclass
class DataHubConnector:
    """Wrapper around DataHub SDK for metadata operations."""

    server: str
    token: str
    _client: Optional[DataHubClient] = None
    _collector: Optional[ContextCollector] = None
    _writer: Optional[DataHubWriter] = None

    def __post_init__(self):
        self._client = DataHubClient(
            server=self.server,
            token=self.token,
        )
        self._collector = ContextCollector(self._client)
        self._writer = DataHubWriter(self._client)

    def verify(self) -> bool:
        """Test connectivity by listing URNs."""
        try:
            list(self._client.search.get_urns("*"))
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    @property
    def client(self) -> DataHubClient:
        """Access the raw DataHubClient."""
        return self._client

    @property
    def collector(self) -> ContextCollector:
        """Access the context collector."""
        return self._collector

    @property
    def writer(self) -> DataHubWriter:
        """Access the DataHub writer (mutations)."""
        return self._writer
