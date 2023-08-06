# client.py  
import socket
import sys 

package_server_ip='10.196.6.228'

# create a socket object
def Message(inputToFunction):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    server_address = (package_server_ip, 10002)
    print >>sys.stderr, 'connecting to %s port %s' % server_address
    # connection to hostname on the port.
    sock.connect(server_address)                               
    try:
        #Send data
        message = inputToFunction
        print >>sys.stderr, 'sending "%s"' % message
        sock.sendall(message)

        #Look for the response
        amount_received = 0
        amount_expected = len(message)
        while amount_received < amount_expected:
            if(message == 'CCC'):
                break
            data = sock.recv(3)
            amount_received += len(data)
            print >>sys.stderr, 'received "%s"' % data

    finally:
        print >>sys.stderr, 'closing socket'
        sock.close()
    



