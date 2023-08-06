# pylint: disable=C0103, F0401
from ldap3 import Connection, Server, ALL

def connect(server_ip, port, ssl=False):
    """
    Connects to AD instance using ldap3

    Args:
        string server_ip  the server ip address
        int port
        optional bool ssl
    Returns:
        server connection object
    Raises:
        Exception if server_ip is None
        Exception if port is None
    """
    if not server_ip:
        raise Exception("Invalid server IP address.")
    if not port:
        raise Exception("Invalid port encountered when connecting to server.")

    # instantiate server object
    return Server(server_ip, port=port, get_info=ALL, use_ssl=ssl)

def auth(server, usr, psw):
    """
    Authenticates user against ad server using ldap3

    Args:
        object server  the server object
        string usr  the username
        string psw  the password
    Returns:
        bool whether the user exists
    Raises:
        Exception if server object is None
    """
    if not server:
        raise Exception("Invalid server object. Pass valid server object retrieved from connect()")

    try:
        # connect to ad
        conn = Connection(server, authentication='SIMPLE', client_strategy='SYNC',\
            raise_exception=True, user=usr, password=psw)
        # open a connection
        conn.bind()
    except Exception as e:
        print (e)
        return False

    return True
