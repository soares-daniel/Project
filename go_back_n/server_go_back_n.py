import json
import random
import socket
import time
import logging
from logging import handlers

def server (process_id: int, num_processes: int, filename: str, probability: float, window_size: int, chunk_size: int, buffer_size: int):
    """Server function to send the file to the clients using the Selective-Repeat protocol"""

    logger = logging.getLogger(f"Server_{process_id}")
    logger.setLevel(logging.DEBUG)
    file_handler = handlers.TimedRotatingFileHandler(f"logs/server_{process_id}.log", when="midnight", interval=1, backupCount=7, encoding="utf-8")
    formatter = logging.Formatter('%(asctime)s - %(levelname)-8s - %(name)s - %(message)s')
    stream_handler = logging.StreamHandler()
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.ERROR)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    # Create and start the server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_addr = ("127.0.0.1", 10000 + int(process_id))
    server_socket.bind(server_addr)

    # Bytes stats
    bytes_sent: int = 0
    bytes_received: int = 0

    # Wait for all clients to connect
    ready_clients: list[tuple] = []
    while len(ready_clients) < int(num_processes):
        data, address = server_socket.recvfrom(buffer_size)
        bytes_received += len(data)
        logger.debug(f"Received {len(data)} bytes from {address}")
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
        bytes_sent += server_socket.sendto(bytes(str(len(packets)), "utf-8"), client)
        logger.debug(f"Sent amount of packets to {client}")

    # Send the file to all clients
    packets_sent = 0
    retransmissions_sent = 0
    sent_packets: dict[tuple, list[bytes]] = {}
    for client in ready_clients:
        sent_packets[client] = []
    seq_num: int = 0
    window_start: int = 0
    window_end = window_size - 1
    datagram_seq_num = window_start
    while seq_num < len(packets):
        # Send the window
        for client in ready_clients:
            # Set first seq_num for this datagram
            seq_num = datagram_seq_num
            # Send the packet to all clients
            for _ in range(window_size):
                packet = packets[seq_num]
                if probability < random.random():
                    # Pack the packet with the seq_num into a message
                    message = f"{seq_num} {packet}".encode("utf-8")
                    bytes_sent += server_socket.sendto(message, client)
                    sent_packets[client].append(packet)
                    logger.debug(f"Sent packet {seq_num}/{len(packets)} to {client}")
                else:
                    logger.debug(f"Packet {seq_num} lost")
                packets_sent += 1
                seq_num += 1
        # Wait for acks and resend packets if necessary
        ready_clients = []
        while len(ready_clients) < int(num_processes):
            ack_message, address = server_socket.recvfrom(buffer_size)
            bytes_received += len(ack_message)
            # Check if client has received window_size num of packets
            if int(ack_message.decode()) == window_size:
                ready_clients.append(address)
            # If ack is not for the current packet, don't move the window and resend the packet
            elif int(ack_message.decode()) < window_size:
                seq_num = datagram_seq_num
                for _ in range(window_size):
                    packet = packets[seq_num]
                    if probability < random.random():
                        # Pack the packet with the seq_num into a message
                        message = f"{seq_num} {packet}".encode("utf-8")
                        bytes_sent += server_socket.sendto(message, address)
                        sent_packets[address].append(packet)
                        logger.debug(f"Retransmitted packet {seq_num} to {address}")
                    else:
                        logger.debug(f"Packet {seq_num} lost")
                    packets_sent += 1
                    bytes_sent += len(packet)
                    seq_num += 1
                retransmissions_sent += 1
        # Move the window
        window_start += window_size
        datagram_seq_num = window_start
        window_end += window_size
        if window_end >= len(packets):
            window_end = len(packets) - 1
            window_size = window_end - window_start + 1

    # Send the client that the last packet is sent
    for client in ready_clients:
        bytes_sent += server_socket.sendto(b"eof", client)
        logger.debug(f"Sent eof to {client}")

    end_time = time.time()

    # Close the socket
    server_socket.close()

    time.sleep(1)

    # Sent stats to stats json
    delta_time = end_time - start_time
    stats = {
        "type": "Server",
        "process": process_id,
        "time": delta_time,
        "packets_sent": packets_sent,
        "bytes_sent": bytes_sent,
        "bytes_received": bytes_received,
        "retransmissions_sent": retransmissions_sent,
    }
    with open("stats.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    data["processes"].append(stats)
    with open("stats.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
