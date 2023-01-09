import random
import socket
import time

def server (process_id: int, num_processes: int, filename: str, probability: float, protocol: str, window_size: int):

    # Create and start the server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_addr = ("127.0.0.1", 10000 + int(process_id))
    server_socket.bind(server_addr)

    # Wait for all clients to connect
    ready_clients: list[tuple] = []
    while len(ready_clients) < int(num_processes):
        data, address = server_socket.recvfrom(1024)
        print(f"received {len(data)} bytes from {address}")
        if data == b"hello":
            ready_clients.append(address)

    # Prepare the packets
    packets: list[bytes] = []
    with open(filename, "rb") as file:
        while True:
            data = file.read(1024)
            if not data:
                break
            packets.append(data)

    start_time = time.time()

    # Send the amount of packets to the clients
    for client in ready_clients:
        server_socket.sendto(bytes(str(len(packets)), "utf-8"), client)

    # Send the file to all clients
    sent_packets = 0
    packets_sent: dict[tuple, list[bytes]] = {}
    for client in ready_clients:
        packets_sent[client] = []
    seq_num: int = 0
    window_start: int = 0
    window_end = window_size - 1
    while seq_num < len(packets):
        # Send the window
        while window_start <= window_end:
            # Take the packet but don't remove it from packets, as it can be, that it fails to be send, so you need to send it again.
            if window_start >= len(packets):
                break
            packet = packets[window_start]
            # Send the packet to all clients
            for client in ready_clients:
                if probability < random.random():
                    # Pack the packet with the seq_num into a message
                    message = f"{seq_num} {packet}".encode("utf-8")
                    server_socket.sendto(message, client)
                    packets_sent[client].append(packet)
                    print(f"Sent packet {seq_num} to {client}")
                    sent_packets += 1
                    seq_num += 1
                    window_start += 1
                else:
                    continue # Packet lost
        # Wait for acks and resend packets if necessary
        ready_clients = []
        while len(ready_clients) < int(num_processes):
            data, address = server_socket.recvfrom(1024)
            # Check if the ack is for the current packet
            if int(data.decode()) == window_end:
                ready_clients.append(address)
            # If ack is not for the current packet, don't move the window and resend the packet
            elif int(data.decode()) <= seq_num - 1:
                seq_num = window_start
                while window_start <= window_end:
                    packet = packets[window_start]
                    if probability < random.random():
                        # Pack the packet with the seq_num into a message
                        message = f"{seq_num} {packet}".encode("utf-8")
                        server_socket.sendto(message, address)
                        packets_sent[address].append(packet)
                        print(f"Sent packet {seq_num} to {address}")
                        sent_packets += 1
                        seq_num += 1
        # Move the window
        window_start = window_end + 1
        window_end += window_size
        if window_end >= len(packets):
            window_end = len(packets) - 1

    # Send the client that the last packet is sent
    for client in ready_clients:
        server_socket.sendto(b"eof", client)
        print(f"Sent eof to {client}")

    end_time = time.time()

    # Close the socket
    server_socket.close()

    # Print stats
    print(f"Sent {sent_packets} packets in {end_time - start_time} seconds")
