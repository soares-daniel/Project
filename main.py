import sys
from server import Server

def main() -> None:
    """Main function"""
    # Parse command line arguments
    id_process = int(sys.argv[1])
    num_processes = int(sys.argv[2])
    filename = sys.argv[3]
    probability = float(sys.argv[4])
    protocol = sys.argv[5]
    window_size = int(sys.argv[6])

    # Create a server
    server = Server(num_processes, probability, protocol, window_size, filename)

    # Run the server
    server.run()

    # Create clients

if __name__ == '__main__':
    main()
