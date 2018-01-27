import socket

from os import getcwd
from sys import exit, stdout


from Output import Output
from Client import Client


HOST_NUMBER = 8000
BACKLOG = 1


if __name__ == "__main__":

    output = Output(stdout)

    current_path = getcwd()
    sock = socket.socket()

    while True:
        try:
            # connect to the HOST
            sock.bind(("", HOST_NUMBER))
            output.success("Connected to the host: http://127.0.0.1:{host}/".format(host=HOST_NUMBER))
            break
        except OSError as e:
            HOST_NUMBER += 1    # if HOST is busy we try to connect the other one
        except:
            output.error("Something wrong with the connection to the server")   # unexpected error
            exit()

    sock.listen(BACKLOG)

    try:
        while True:
            conn, adr = sock.accept()
            client = Client(conn, adr, current_path, output=output)
            current_path = client.do()
            del client
            conn.close()
    except KeyboardInterrupt:
        output.success("Disconnected")
        sock.shutdown(1)
    except BrokenPipeError as e:
        output.error("Something wrong with the connection to the server\n{error}".format(error=e))
        sock.shutdown(1)
