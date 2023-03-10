import random
import socket
import time

def server (process_id: int, num_processes: int, filename: str, probability: float, window_size: int, chunk_size: int):
    """Server function to send the file to the clients using the Go-Back-N protocol"""
    # Create and start the server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_addr = ("127.0.0.1", 10000 + int(process_id))
    server_socket.bind(server_addr)

    # Wait for all clients to connect
    ready_clients: list[tuple] = []
    while len(ready_clients) < int(num_processes):
        data, address = server_socket.recvfrom(chunk_size)
        print(f"received {len(data)} bytes from {address}")
        if data == b"hello":
            ready_clients.append(address)

    # Prepare the packets
    packets: list[bytes] = []
    # If file is txt use r else rb
    with open(filename, "rb") as file:
        while True:
            packet = file.read(chunk_size)
            if packet == b"":
                break
            packets.append(packet)

    start_time = time.time()

    # Send the amount of packets to the clients
    for client in ready_clients:
        server_socket.sendto(bytes(str(len(packets)), "utf-8"), client)
        print(f"Sent amount of packets to {client}")

    # Send the file to all clients
    unack_packets: dict[tuple, list[int]] = {}
    packets_sent = 0
    sent_packets: dict[tuple, list[bytes]] = {}
    for client in ready_clients:
        sent_packets[client] = []
        unack_packets[client] = []
    seq_num: int = 0
    window_start: int = 0
    window_end = window_size - 1
    datagram_seq_num = window_start
    while seq_num < len(packets):
        # Send the window
        for client in ready_clients:
            # Set first seq_num for this datagram
            window_start = datagram_seq_num
            seq_num = datagram_seq_num
            # Send the packet to all clients
            for _ in range(window_size):
                if window_start > len(packets) - 1:
                    continue
                packet = packets[seq_num]
                if probability < random.random():
                    # Pack the packet with the seq_num into a message
                    message = f"{seq_num} {packet}".encode("utf-8")
                    server_socket.sendto(message, client)
                    sent_packets[client].append(packet)
                    print(f"Sent packet {seq_num}/{len(packets)} to {client}")
                else:
                    print(f"Packet {seq_num} lost")
                unack_packets[client].append(seq_num)
                packets_sent += 1
                seq_num += 1
                window_start += 1
        # Wait for acks and resend packets if necessary
        ready_clients = []
        while True:
            ack_message, address = server_socket.recvfrom(chunk_size)
            # Covert ack_message to list[int]
            if ack_message == b"[]":
                ack_packets = []
            else:
                print(ack_message)
                #! Blocks when the first client is done
                # FIXME
                ack_packets = [int(x) for x in ack_message.decode()[1:-1].split(", ")]
                ack_packets = list(dict.fromkeys(ack_packets)) # Remove duplicates
            for index in ack_packets:
                if index in unack_packets[address]:
                    unack_packets[address].remove(index)
            if len(unack_packets[address]) == 0:
                ready_clients.append(address)
            # !If ack is not for the current packet, don't move the window and resend the packet
            else:
                # Retransmit missing packets
                for missing in unack_packets[address]:
                    packet = packets[missing]
                    if probability < random.random():
                        # Pack the packet with the seq_num into a message
                        message = f"{missing} {packet}".encode("utf-8")
                        server_socket.sendto(message, address)
                        print(f"Resent packet {missing} to {address}")
                        packets_sent += 1
            if len(ready_clients) == int(num_processes):
                break
        # Move the window
        window_start = window_end + 1
        datagram_seq_num = window_start
        window_end += window_size
        if window_end >= len(packets):
            window_end = len(packets) - 1

    # Send the client that the last packet is sent
    for client in ready_clients:
        server_socket.sendto(b"eof", client)
        print(f"Sent eof to {client}")

    # Wait for all clients to finish
    ready_clients = []
    while len(ready_clients) < int(num_processes):
        data, address = server_socket.recvfrom(chunk_size)
        print(f"received {len(data)} bytes from {address}")
        if data == b"ok":
            ready_clients.append(address)

    end_time = time.time()

    # Close the socket
    server_socket.close()

    # Print stats
    print(f"Sent {packets_sent} packets in {end_time - start_time} seconds")
