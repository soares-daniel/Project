"""New version"""

import socket
import argparse
import random

# Parse the command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument("id_process", type=int, help="Number of the current process")
parser.add_argument("number_of_processes", type=int, help="Total number of clients that will join the communication")
parser.add_argument("filename", type=str, help="Name of file to be send to each client that is connected to this server")
parser.add_argument("probability", type=float, help="Probability of an UDP send not to be successful")
parser.add_argument("protocol", type=str, choices=["go-back-n", "selective-repeat"], help="Protocol to use")
parser.add_argument("window_size", type=int, help="The size of the window for Go-Back-N")
args = parser.parse_args()

# Create the UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Set the timeout for the socket
sock.settimeout(1.0)

# Open the file to be transmitted
with open(args.filename, "rb") as f:
    # Read the file into a bytes object
    file_data = f.read()

# Divide the file into packets
packet_size = 1024
num_packets = len(file_data) // packet_size + 1
packets = [(i, file_data[i*packet_size:(i+1)*packet_size]) for i in range(num_packets)]

# Set the starting sequence number
seq_num = 0

# Keep track of the number of bytes and packets sent and received, and the number of retransmissions
bytes_sent = 0
packets_sent = 0
bytes_received = 0
packets_received = 0
retransmissions_received = 0
retransmissions_sent = 0

# Create a list to store the packets that have been sent
sent_packets = []

# Create a set to store the clients that are ready
ready_clients = set()

while True:
    # Wait for all clients to join the session
    while len(sent_packets) > 0:
        try:
            # Receive a message from a client
            data, addr = sock.recvfrom(1024)
            # If the message is a "ready" message, add the client to the list of ready clients
            if data == b"ready":
                ready_clients.add(addr)
            # If the message is an acknowledgement message, remove the corresponding packet from the list of sent packets
            else:
                ack_num = int(data)
                sent_packets = [p for p in sent_packets if p[0] != ack_num]
        except socket.timeout:
            # If we time out, resend all the packets in the window
            for packet in sent_packets:
                sock.sendto(packet[1], packet[2])
                retransmissions_sent += 1

    # Check if all clients are ready
    if len(ready_clients) == args.number_of_processes:
        # Send the packets to all clients
        for packet in packets:
            # Check if the send should be successful or not
            if random.random() > args.probability:
                # Send the packet to all clients
                for client in ready_clients:
                    sock.sendto(packet[1], client)
                    bytes_sent += len(packet[1])
                    packets_sent += 1
                # Add the packet to the list of sent packets
                sent_packets.append((packet[0], packet[1], ready_clients))
        # Clear the list of ready clients
        ready_clients.clear()

    # Wait for acknowledgement messages
    if args.protocol == "go-back-n":
        while len(sent_packets) > 0:
            try:
                # Receive an acknowledgement message
                data, addr = sock.recvfrom(1024)
                ack_num = int(data)
                # If the acknowledgement is for the first packet in the window, remove it from the list
                if sent_packets[0][0] == ack_num:
                    sent_packets.pop(0)
                # Update the sequence number
                seq_num = ack_num + 1
            except socket.timeout:
                # If we time out, resend all the packets in the window
                for packet in sent_packets:
                    sock.sendto(packet[1], packet[2])
                    retransmissions_sent += 1
    elif args.protocol == "selective-repeat":
        while len(sent_packets) > 0:
            try:
                # Receive an acknowledgement message
                data, addr = sock.recvfrom(1024)
                ack_num = int(data)
                # Remove the acknowledged packet from the list of sent packets
                sent_packets = [p for p in sent_packets if p[0] != ack_num]
            except socket.timeout:
                pass

    # Check if all packets have been received
    if packets_received == num_packets:
        break

# Close the socket
sock.close()

# Print the results
print("Total number of bytes received:", bytes_received)
print("Total number of packets received:", packets_received)
print("Total number of bytes sent:", bytes_sent)
print("Total number of packets sent:", packets_sent)
print("Number of retransmissions received:", retransmissions_received)
print("Number of retransmissions sent:", retransmissions_sent)
