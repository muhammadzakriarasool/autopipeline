"""DataHub connector — wraps the SDK client and exposes collector + writer."""

from dataclasses import dataclass
from datahub.sdk.main_client import DataHubClient
from autopipeline.context import ContextCollector
from autopipeline.writer import DataHubWriter


@dataclass
class DataHubConnector:
    server: str
    token: str
    _client: DataHubClient = None
    _collector: ContextCollector = None
    _writer: DataHubWriter = None

    def __post_init__(self):
        self._client = DataHubClient(server=self.server, token=self.token)
        self._collector = ContextCollector(self._client)
        self._writer = DataHubWriter(self._client)

    def verify(self) -> bool:
        try:
            list(self._client.search.get_urns("*"))
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    @property
    def client(self):
        return self._client

    @property
    def collector(self):
        return self._collector

    @property
    def writer(self):
        return self._writer
