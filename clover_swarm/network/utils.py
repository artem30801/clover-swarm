import socket

import trio


async def get_ip():
    """
    Returns the IP address of current computer or `127.0.0.1` if no network connection present.
    """
    ip_socket = trio.socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        await ip_socket.connect(("8.8.8.8", 80))  # google dns, but might be any unreachable address
        return ip_socket.getsockname()[0]
    except socket.error:
        return "127.0.0.1"  # localhost
    finally:
        ip_socket.close()


async def get_local_ip():
    pass
