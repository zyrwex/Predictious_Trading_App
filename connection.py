"""A supporting module with various functions that help establish the connection"""

import threading
from TradingApp import TradingApp


def create_file(ip, port, client_id):
    """Save the user inputs connection data

    :param ip: IP number
    :param port: Port number (Paper Trading Account port of TWS is 7497)
    :param client_id: Client ID (TWS session can handle 32 different clients simultaneously)
    """
    f = open("connection_data.txt", "w")
    f.write(""+str(ip)+","+str(port)+","+str(client_id)+"")
    f.close()


def read_file():
    """This function is used to set default values in the entry boxes in the GUI

    :return: connection information as a list
    """

    try:
        f = open("connection_data.txt", "r")
        lst = f.read().split(',')
        f.close()
        return lst
    except IOError:  # If file doesn't exist, create a new one
        f = open("connection_data.txt", "w+")
        f.write("127.0.0.1,7497,0")
        lst = f.read().split(',')
        f.close()
        return lst


def tws_connect():
    """Establish a connection to TWS"""

    def websocket_con():
        """Start TCP connection. This is where the message queue is processed in an
        infinite loop and the EWrapper call-back functions are automatically triggered
        """

        app.run()

    # Open the file with the connection information
    f = open("connection_data.txt", "r")
    lst = f.read().split(',')
    # Initialize Trading Object
    app = TradingApp()
    # Connect to local machine
    app.connect(lst[0], int(lst[1]), int(lst[2]))
    f.close
    # Put websocket connection into another thread
    con_thread = threading.Thread(target=websocket_con, daemon=True)
    con_thread.start()

    # Check the connection
    if app.isConnected() is True:
        return True
    else:
        # if connection failed, set connection data to default values
        f = open("connection_data.txt", "w")
        f.write("127.0.0.1,7497,0")
        f.close()
        return False
