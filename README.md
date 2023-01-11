# Project - Implementing an efficient many to many communication protocol over UDP

The goal of this project is to implement a communication among multiple participants.

A given number of clients connect to a server and download a file using the go-back-n protocol.


### How to start:

**Arguments:**

* `id_process`: The number of the current server process
* `num_of_processes`: Total number of clients that will join this communication
* `filename`: Name of file to be send to each client that is connected to this server
* `probability`: Probability of an UDP send not to be successful - this is to simulate network errors and thus retransmissions

Start:

```
python main.py id process numb_of_processes filename probability protocol window_size
```

Example:

```
python main.py 2 1 50MB.zip 0.2 Go-Back-N 5
```
