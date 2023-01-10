import socket

def client(server_process_id: int, client_process_id: int, filename: str, window_size: int, chunk_size: int):
    """Client function to send a file to the server using the Go-Back-N Protocol"""
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

    # Receive the file
    window_start: int = 0
    window_end: int = window_size - 1
    received_packets: dict[int,bytes] = {}
    ack_num = 0
    client_socket.settimeout(0.1)
    # while slient is connected to server
    while ack_num < num_packets - 1:
        for i in range(window_size):
            try:
                message, address = client_socket.recvfrom(chunk_size)
                if message == b"eof":
                    break
            except socket.timeout:
                # Send ack if no new message
                continue
            if address == server_addr:
                # Packet received
                seq_num, data = message.decode().split(" ", 1)
                seq_num = int(seq_num)
                data = bytes(data, "utf-8")
                received_packets[seq_num] = data
                print(f"Received packet {seq_num} from {address}")
                ack_num = len(received_packets) - 1
                window_start += 1
        # Send acks
        client_socket.sendto(bytes(str(len(received_packets)), "utf-8"), server_addr)
        print(f"Sent ack {ack_num} to {server_addr}")
        if ack_num == len(received_packets) - 1:
            window_start = window_end + 1
            window_end = window_start + window_size - 1
            if window_end > num_packets:
                window_end = num_packets - 1

    # Write the file
    with open(f"received_data/client_{client_process_id}_{filename}", "wb") as file:
        for i in range(len(received_packets) - 1):
            file.write(received_packets[i])

    # Close the socket
    client_socket.close()
