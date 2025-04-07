import contextlib
from typing import TypeVar

from mcp.shared.memory import create_connected_server_and_client_session
from typing_extensions import Unpack

from fastmcp.clients.base import BaseClient, ClientKwargs
from fastmcp.server.server import FastMCP

T = TypeVar("T")


class FastMCPClient(BaseClient):
    """Client that connects directly to an in-memory FastMCP server.

    This client creates and manages an in-memory connection to a server,
    without using any external processes or network connections.
    """

    def __init__(
        self,
        server: FastMCP,
        **kwargs: Unpack[ClientKwargs],
    ):
        """Initialize an InMemoryClient that connects to an in-memory MCP server.

        Args:
            server: The FastMCP instance to connect to
            **kwargs: Additional arguments for BaseClient
        """
        super().__init__(**kwargs)
        self.server = server
        self._cm_session = None

    @contextlib.asynccontextmanager
    async def _connect(self):
        """Set up in-memory connection and session"""
        self._cm_session = create_connected_server_and_client_session(
            server=self.server._mcp_server,
            read_timeout_seconds=self._read_timeout_seconds,
            sampling_callback=self._sampling_callback,
            list_roots_callback=self._list_roots_callback,
            logging_callback=self._logging_callback,
            message_handler=self._message_handler,
        )

        async with self._cm_session as session:
            # No need to call initialize as create_connected_server_and_client_session already does
            async with self._set_session((None, None), session):
                yield self
