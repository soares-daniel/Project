import socket
import random
import threading

class Server:
    """A server that sends a file to multiple clients using UDP"""

    def __init__(self, host, port, window_size, probability, filename) -> None:
        self.host = host
        self.port = port
        self.window_size = window_size
        self.probability = probability
        self.filename = filename
        self.ack_num = 0
        self.seq_num = 0
        self.unacknowledged_packets = {}
        self.next_packet_to_send = b"Hello, Client!"
        self.packets_sent = {}
        self.total_packets_sent = 0
        self.bytes_received = {}
        self.total_bytes_received = 0

        # Create the socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))

    def run(self) -> None:
        """Wait for clients to connect and then send them a file"""

        print("Waiting for clients to connect...")

        # Create a list to store the client addresses
        client_list = []

        while True:
            # Wait for a client to connect
            client_addr, _ = self.sock.recvfrom(1024)
            print(f"Client connected from {client_addr}")

            # Add the client's address to the list
            client_list.append(client_addr)

            # Start a new thread to handle the client
            t = threading.Thread(target=self.handle_client, args=(client_addr,))
            t.start()

    def handle_client(self, client_addr) -> None:
        """Send a file to a client and track performance metrics"""

        # Send the file to the client
        self.send_file(self.filename, client_addr)

        # Measure the performance metrics
        self.measure_performance()

    def send_packet(self, data, addr) -> None:
        """The sliding window protocol"""

        # Check if the window is full
        if self.seq_num - self.ack_num >= self.window_size:
            # Wait for an acknowledgement from the client
            data, addr = self.sock.recvfrom(1024)
            self.ack_num = int(data.decode())

        # Send the packet and increment the sequence number
        success = self.send_packet_with_probability(data, addr)
        if success:
            self.seq_num += 1
            self.unacknowledged_packets[self.seq_num] = data
        else:
            # Handle retransmission
            pass

    def send_packet_with_probability(self, data, addr) -> bool:
        """Send a packet with a probability of failure"""

        # Generate a random number between 0 and 1
        p = random.uniform(0, 1)

        # If the probability of success is greater than the probability of failure,
        # send the packet
        if p > self.probability:
            self.sock.sendto(data, addr)
            return True
        else:
            return False

    def send_file(self, filename, addr) -> None:
        """Send a file to the client using the Go-back-N protocol"""

        # Open the file in binary mode
        with open(filename, "rb") as f:
            # Read the file in chunks of 1024 bytes
            chunk = f.read(1024)

            # Keep sending the file until all the data has been sent
            while chunk:
                # Send the chunk of data to the client
                self.send_packet(chunk, addr)

                # Wait for an acknowledgement from the client
                data, _ = self.sock.recvfrom(1024)
                self.ack_num = int(data.decode())

                # If the acknowledgement is not the expected one,
                # retransmit all the unacknowledged packets
                if self.ack_num < self.seq_num:
                    for i in range(self.ack_num, self.seq_num):
                        self.send_packet(self.unacknowledged_packets[i], addr)
                else:
                    self.unacknowledged_packets = {}

                # Read the next chunk of data from the file
                chunk = f.read(1024)

    def measure_performance(self) -> None:
        """Track the number of packets sent and the number of bytes received"""

        # Run the main loop of the server
        while True:
            # Wait for a connection from a client
            data, client_addr = self.sock.recvfrom(1024)

            client = f"{client_addr[0]}:{client_addr[1]}"

            # Increment the packet sent counter
            self.packets_sent[client] += 1
            self.total_packets_sent += 1

            # Increment the bytes received counter
            self.bytes_received[client] += len(data)
            self.total_bytes_received += len(data)
