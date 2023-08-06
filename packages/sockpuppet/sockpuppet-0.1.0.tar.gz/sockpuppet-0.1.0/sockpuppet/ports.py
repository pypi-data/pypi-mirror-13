from socket import socket, create_connection, error as socket_error
from time import sleep


def find_free_port(address=''):
    s = socket()
    s.bind((address, 0))
    _, port = s.getsockname()
    return port


def wait_for_server(port, address='127.0.0.1', timeout=5, poll_frequency=0.05):
    waited = 0
    while waited < timeout:
        try:
            create_connection((address, port))
        except socket_error as e:
            if 'connection refused' not in e.strerror.lower():
                raise
        else:
            return
        sleep(poll_frequency)
        waited += poll_frequency
    raise AssertionError('server on {}:{} did not start within {}s'.format(
        address, port, timeout
    ))

