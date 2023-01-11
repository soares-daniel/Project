import socket

def client(server_process_id: int, client_process_id: int, filename: str, window_size: int, chunk_size: int):
    """Client function to send a file to the server using the Selective-Repeat Protocol"""
    # Create and start the client
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_addr: tuple = ("127.0.0.1", 9000 + int(client_process_id))
    client_socket.bind(client_addr)

    server_addr: tuple = ("127.0.0.1", 10000 + int(server_process_id))

    # Send hello to server
    client_socket.sendto(b"hello", server_addr)

    # Receive the amount of packets
    message, address = client_socket.recvfrom(1024)
    num_packets: int = int(message.decode())

    # Receive the file using Selective Repeat
    ack_packets: list[int] = []
    window_start: int = 0
    window_end: int = window_size - 1
    received_packets: dict[int,bytes] = {}
    ack_num = 0
    client_socket.settimeout(0.1)
    # While not all packets received
    while True:
        for _ in range(window_size):
            try:
                message, address = client_socket.recvfrom(chunk_size)
                if message == b"eof":
                    break
            except socket.timeout:
                # Send ack if no new message
                continue
            pack_num, data = message.decode().split(" ", 1)
            pack_num = int(pack_num)
            data = bytes(data, "utf-8")
            received_packets[pack_num] = data
            print(f"Received packet {pack_num} from {address}")
            ack_num = len(received_packets) - 1
            ack_packets.append(pack_num)
        # Send acks
        ack_message = f"{ack_packets}".encode("utf-8")
        client_socket.sendto(ack_message, server_addr)
        # If all packets within window received, move window and reset ack_packets
        if len(ack_packets) == window_end - window_start + 1:
            window_start = ack_num + 1
            window_end = window_start + window_size - 1
        ack_packets = []
        if len(received_packets) == num_packets:
            break

    # Write the file
    with open(f"received_data/client_{client_process_id}_{filename}", "wb") as file:
        for i in range(len(received_packets) - 1):
            file.write(received_packets[i])

    # send ok to server
    if len(received_packets) == num_packets:
        client_socket.sendto(b"ok", server_addr)
        print(f"Sent ok to {server_addr}")

    # Close the socket
    client_socket.close()
