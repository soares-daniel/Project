import socket

def client(server_process_id: int, client_process_id: int, filename: str, probability: float, protocol: str, window_size: int):

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
    packets_received: int = 0
    ack_num = 0
    # while slient is connected to server
    while packets_received < num_packets:
        while window_start <= window_end:
            message, address = client_socket.recvfrom(1024)
            if address == server_addr:
                # End of file
                if message == b"eof":
                    break
                # Packet received
                else:
                    seq_num, data = message.decode().split(" ", 1)
                    seq_num = int(seq_num)
                    data = bytes(data, "utf-8")
                    received_packets[seq_num] = data
                    print(f"Received packet {seq_num} from {address}")
                    ack_num = seq_num
                    packets_received += 1
                    window_start += 1
        # Send acks
        client_socket.sendto(bytes(str(ack_num), "utf-8"), server_addr)
        print(f"Sent ack {ack_num} to {server_addr}")
        if ack_num == len(received_packets) - 1:
            window_start = window_end + 1
            window_end = window_start + window_size - 1
            if window_end > num_packets:
                window_end = num_packets - 1

    # Write the file
    with open(f"received_data/client_{client_process_id}_{filename}", "wb") as file:
        for i in range(packets_received):
            file.write(received_packets[i])

    # Close the socket
    client_socket.close()
