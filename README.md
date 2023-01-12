# Project - Implementing an efficient many to many communication protocol over UDP

The goal of this project is to implement a communication among multiple participants.

A given number of clients connect to a server and download a file using the go-back-n and the selective-repeat protocol.

**NOTE:** Selective-Repeat is currently not working

## Requirements

**NOTE:** If the following commands don't work, try to user ```python3``` instead of  ```python``` and ```pip3```instead of ```pip```.

It is best to create a virtual environment to avoid conflicts between different versions of libraries or python.

This can be done via the command:

```python
python -m venv .venv
```

Based on your shell and platform, the command, to activate your environment can be different.
For bash/zsh it would be:

```bash
source .venv/bin/activate
```

As this project uses 3rd party libraries, you should install these using ``pip`` and the **requirements.txt** with the following command:

```python
pip install -r requirements.txt
```

After **crcmod** and **tabulate** are installed you are good to go!

## How to start

**Arguments:**

* `id_process`: The number of the current server process
* `num_of_processes`: Total number of clients that will join this communication
* `filename`: Name of file to be send to each client that is connected to this server
* `probability`: Probability of an UDP send not to be successful - this is to simulate network errors and thus retransmissions

Start:

```python
python main.py id process numb_of_processes filename probability protocol window_size
```

Example:

```python
python main.py 2 1 50MB.zip 0.2 Go-Back-N 5
```

## Contact

Discord: **Sedamaso#5217**

Email: [sedam.code@gmail.com](mailto:sedam.code@gmail.com
