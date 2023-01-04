import socket

class Client:
    """Client class for connecting to the server and recieving data from it."""
    def __init__(self, process_id, server_addr, window_size, protocol, probability) -> None:
        self.process_id = process_id
        self.server_addr = server_addr
        self.window_size = window_size
        self.protocol = protocol
        self.probability = probability

    def run(self) -> None:
        """Connect to the server and recieve data from it."""

    def recieve_packet(self) -> None:
        """Recieve a packet from the server."""


    def send_ack(self) -> None:
        """Send an acknowledgement to the server."""


    def write_to_file(self) -> None:
        """Write the recieved data to a file."""

