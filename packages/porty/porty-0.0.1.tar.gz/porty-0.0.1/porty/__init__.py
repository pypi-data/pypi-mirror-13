import random
import socket


def getPort(minPort, maxPort):
    ports = list(range(minPort, maxPort))
    random.shuffle(ports)
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('', port))
            sock.close()
            return port
        except socket.error:
            pass
    raise RuntimeError('could not bind to a port')
