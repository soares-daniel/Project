import sys
import threading
from server import server
from client import client

def main():
    #Parse the args
    process_id: int = int(sys.argv[1])
    num_processes: int = int(sys.argv[2])
    filename: str = sys.argv[3]
    probability: float = float(sys.argv[4])
    protocol: str = sys.argv[5]
    window_size: int = int(sys.argv[6])

    # Create and start the server
    server_thread = threading.Thread(target=server, args=(process_id, num_processes, filename, probability, protocol, window_size))
    server_thread.start()

    # Create and start the clients
    client_threads = []
    for i in range(num_processes):
        client_thread = threading.Thread(target=client, args=(process_id, i, filename, probability, protocol, window_size))
        client_thread.start()
        client_threads.append(client_thread)

if __name__ == "__main__":
    main()
