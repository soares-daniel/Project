# pylint: disable=C0415
import sys
import threading

def main():
    """Main function to start server and clients"""
    #Parse the args
    process_id: int = int(sys.argv[1])
    num_processes: int = int(sys.argv[2])
    filename: str = sys.argv[3]
    probability: float = float(sys.argv[4])
    protocol: str = sys.argv[5]
    window_size: int = int(sys.argv[6])

    # Import given protocol
    if protocol == "Go-Back-N":
        from go_back_n import server
        from go_back_n import client
    elif protocol == "Selective-Repeat":
        from selective_repeat import server
        from selective_repeat import client
    else:
        print("Wrong protocol given.(Use: Go-Back-N or Selective-Repeat)")
        return

    # Set chunk_size & buffer_size
    chunk_size: int = 3072
    buffer_size: int = 10240

    # Create and start the server
    server_thread = threading.Thread(target=server, args=(process_id, num_processes, filename, probability, window_size, chunk_size, buffer_size))
    server_thread.start()

    # Create and start the clients
    client_threads = []
    for i in range(num_processes):
        client_thread = threading.Thread(target=client, args=(process_id, i, filename, window_size, buffer_size))
        client_thread.start()
        client_threads.append(client_thread)

if __name__ == "__main__":
    main()
