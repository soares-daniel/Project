import json
import socket
import logging
from logging import handlers
import time

def client(server_process_id: int, client_process_id: int, filename: str, window_size: int, buffer_size: int):
    """Client function to send a file to the server using the Go-Back-N Protocol"""

    # Set up logging
    logger = logging.getLogger(f"Client_{client_process_id}")
    logger.setLevel(logging.DEBUG)
    file_handler = handlers.TimedRotatingFileHandler(f"logs/client_{client_process_id}.log", when="midnight", interval=1, backupCount=7, encoding="utf-8")
    formatter = logging.Formatter('%(asctime)s - %(levelname)-8s - %(name)s - %(message)s')
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.ERROR)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    # Create and start the client
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_addr: tuple = ("127.0.0.1", 9000 + int(client_process_id))
    client_socket.bind(client_addr)

    server_addr: tuple = ("127.0.0.1", 10000 + int(server_process_id))

    bytes_sent: int = 0
    bytes_received: int = 0
    # Send hello to server
    bytes_sent += client_socket.sendto(b"hello", server_addr)

    # Receive the amount of packets
    message, address = client_socket.recvfrom(buffer_size)
    bytes_received += len(message)
    num_packets: int = int(message.decode())

    # Receive the file
    window_start: int = 0
    window_end: int = window_size - 1
    received_packets: dict[int,bytes] = {}
    packets_received: int = 0
    retransmissions_received: int = 0
    recv_within_window: int = 0
    ack_num: int = 0
    # While not all packets received
    while ack_num < num_packets - 1:
        recv_within_window = 0
        for _ in range(window_size):
            client_socket.settimeout(0.1)
            try: # Receive packet
                message, address = client_socket.recvfrom(buffer_size)
                bytes_received += len(message)
            except socket.timeout:
                logger.debug(f"Timed out waiting for packet from {server_addr}")
                continue
            if message == b"eof":
                break
            if address == server_addr:
                # Packet received
                seq_num, data = message.decode().split(" ", 1)
                seq_num = int(seq_num)
                data = bytes(data, "utf-8")
                received_packets[seq_num] = data
                logger.debug(f"Received packet {seq_num} from {address}")
                ack_num = len(received_packets) - 1

                tabs = "\t" * 2 * (client_process_id)

                print(f"{tabs}Client {client_process_id} - {len(received_packets)}", end="\r")
                packets_received += 1
                recv_within_window += 1
        # Send acks
        ack_message = str(recv_within_window).encode("utf-8")
        bytes_sent += client_socket.sendto(ack_message, server_addr)
        logger.debug(f"Sent ack {recv_within_window} to {server_addr}")
        if recv_within_window == window_size:
            # Block while other client are not ready for next datagram
            ready_next = False
            client_socket.setblocking(True)
            while not ready_next:
                message, address = client_socket.recvfrom(buffer_size)
                bytes_received += len(message)
                if message == b"ready":
                    logger.debug(f"Ready for next datagram")
                    client_socket.setblocking(False)
                    ready_next = True
             # Move window
            window_start += window_size
            window_end += window_size
            if window_end > num_packets - 1:
                window_end = num_packets - 1
                window_size = window_end - window_start + 1
        else:
            retransmissions_received += 1

    # Write the file
    with open(f"received_data/client_{client_process_id}_{filename}", "wb") as file:
        for i in range(len(received_packets) - 1):
            file.write(received_packets[i])

    # Close the socket
    client_socket.close()

    time.sleep(1)

    # Sent stats to stats json
    stats = {
        "type": "Client",
        "process": client_process_id,
        "packets_received": packets_received,
        "bytes_sent": bytes_sent,
        "bytes_received": bytes_received,
        "retransmissions_received": retransmissions_received,
    }
    with open("stats.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    data["processes"].append(stats)
    with open("stats.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
