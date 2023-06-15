import pytest
from unittest.mock import MagicMock
import socket
from server import handle_client  # assuming your_file.py contains the handle_client function


@pytest.fixture
def client_fixture():
    conn = MagicMock()
    addr = "127.0.0.1"

    yield conn, addr

    # conn.close.assert_called()


def test_handle_client(client_fixture):
    conn, addr = client_fixture

    # Send a message that should result in a single output line
    conn.recv.side_effect = [
        b"10",  # message length header
        b"SHELL",  # message content
        b"8",  # response length header
        b"Response"  # response content
    ]
    handle_client(conn, addr)

    conn.send.assert_called_with(b"Response")
