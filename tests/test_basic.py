"""Basic tests for PyTTD package"""

import pytest
import sys
import os

# Add the parent directory to the path so we can import pyttd
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_import():
    """Test that we can import the main package"""
    import pyttd

    assert hasattr(pyttd, "OpenTTDClient")
    assert hasattr(pyttd, "__version__")


def test_version():
    """Test that version is defined"""
    import pyttd

    assert pyttd.__version__ == "1.0.0"


def test_client_creation():
    """Test that we can create a client instance without connecting"""
    from pyttd import OpenTTDClient

    client = OpenTTDClient(
        server="127.0.0.1", port=3979, player_name="TestBot", company_name="TestCompany"
    )

    assert client.server == "127.0.0.1"
    assert client.port == 3979
    assert client.player_name == "TestBot"
    assert client.company_name == "TestCompany"
    assert not client.is_connected()


def test_protocol_imports():
    """Test that protocol classes can be imported"""
    from pyttd import Packet, PacketType

    assert Packet is not None
    assert PacketType is not None


def test_game_state_imports():
    """Test that game state classes can be imported"""
    from pyttd import GameState, CompanyInfo, ClientInfo, VehicleInfo, MapInfo

    assert GameState is not None
    assert CompanyInfo is not None
    assert ClientInfo is not None
    assert VehicleInfo is not None
    assert MapInfo is not None


def test_commands_imports():
    """Test that command classes can be imported"""
    from pyttd import Commands, CommandBuilder, CommandPacket, CompanyID

    assert Commands is not None
    assert CommandBuilder is not None
    assert CommandPacket is not None
    assert CompanyID is not None


if __name__ == "__main__":
    pytest.main([__file__])
