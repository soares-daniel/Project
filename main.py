# pylint: disable=C0415
import json
import sys
import threading
import time
import os

from tabulate import tabulate

def main():
    """Main function to start server and clients"""
    #Parse the args
    stats_id: int = int(sys.argv[1])
    num_statses: int = int(sys.argv[2])
    filename: str = sys.argv[3]
    probability: float = float(sys.argv[4])
    protocol: str = sys.argv[5]
    window_size: int = int(sys.argv[6])

    # Create the logs and stats files
    with open("stats_server.json", "w", encoding="utf-8") as file:
        json.dump({}, file, indent=4)
    for i in range(num_statses):
        with open(f"stats_client_{i}.json", "w", encoding="utf-8") as file:
            json.dump({}, file, indent=4)

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

    with open(f"logs/server_{stats_id}.log", "w", encoding="utf-8") as file:
        file.write("")

    # Create and start the server
    server_thread = threading.Thread(target=server, args=(stats_id, num_statses, filename, probability, window_size, chunk_size, buffer_size))
    server_thread.start()

    # Create and start the clients
    client_threads = []
    for i in range(num_statses):
        with open(f"logs/client_{i}.log", "w", encoding="utf-8") as file:
            file.write("")
        client_thread = threading.Thread(target=client, args=(stats_id, i, filename, window_size, buffer_size))
        client_thread.start()
        client_threads.append(client_thread)

    # Wait for the statses to finish
    server_thread.join()
    for client_thread in client_threads:
        client_thread.join()

    print("\n")
    print("All statses finished!")
    print("Printing stats...")
    print()
    time.sleep(2)

    # Create a list with the stats of the server
    with open("stats_server.json", "r", encoding="utf-8") as file:
        stats = json.load(file)
    server_stats = []
    server_stats.append(stats.get("type"))
    server_stats.append(stats.get("process"))
    server_stats.append(stats.get("time"))
    server_stats.append(stats.get("packets_sent"))
    server_stats.append(stats.get("bytes_sent"))
    server_stats.append(stats.get("bytes_received"))
    server_stats.append(stats.get("retransmissions_sent"))

    # Create a list of lists with the stats of each client
    clients: dict[int,list] = {}
    for i in range(num_statses):
        clients[i] = []
        with open(f"stats_client_{i}.json", "r", encoding="utf-8") as file:
            stats = json.load(file)
        client_stats = []
        client_stats.append(stats.get("type"))
        client_stats.append(stats.get("process"))
        client_stats.append(stats.get("packets_received"))
        client_stats.append(stats.get("bytes_sent"))
        client_stats.append(stats.get("bytes_received"))
        client_stats.append(stats.get("retransmissions_received"))
        clients[stats.get("stats")] = client_stats

    table = []
    for i in range(num_statses):
        table.append(clients[i])

    # Print the stats
    print(tabulate([server_stats], headers=["Type", "Process", "Time", "Packets sent", "Bytes sent", "Bytes received", "Retransmissions sent"],
                   tablefmt="psql"))
    print()
    print(tabulate(table, headers=["Type", "Process", "Packets received","Bytes sent", "Bytes received", "Retransmissions received"],
                   tablefmt="psql"))

    # Remove the stats files
    os.remove("stats_server.json")
    for i in range(num_statses):
        os.remove(f"stats_client_{i}.json")

if __name__ == "__main__":
    main()
