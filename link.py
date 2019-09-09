"""link.py: Connects two routers to each other.
Usage: link <name1> <port1> <name2> <port2> <cost>: links router <name1> to
router <name2> with link cost <cost>.
"""

import socket
import sys
from routemsg import *

prompt_for_args = False #set to true to prompt for command line args.

def main():
    if len(sys.argv) == 1:
        print(__doc__)
    elif len(sys.argv) == 6:
        if len(sys.argv[1]) != 1 or len(sys.argv[3]) != 1:
            print('Router names must be single characters!')
            return
        name1, name2 = sys.argv[1], sys.argv[3]

        port1, port2 = 0, 0
        try:
            port1 = int(sys.argv[2])
            port2 = int(sys.argv[4])
        except ValueError:
            print('Port numbers must be integers!')
            return
        
        cost = 0
        try:
            cost = int(sys.argv[5])
        except ValueError:
            print('Link cost must be an integer!')
            return
        if cost <= 0:
            print('Link cost must be positive!')
            return

        linkerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        msg1 = make_routemsg(True, name2, port2, cost)
        msg2 = make_routemsg(True, name1, port1, cost)
        linkerSocket.sendto(msg1, ('127.0.0.1', port1))
        linkerSocket.sendto(msg2, ('127.0.0.1', port2))
        linkerSocket.close()
        
    else:
        print('Invalid usage.')

if __name__ == '__main__':
    if prompt_for_args:
        arglist = input('Enter command line args: ').split()
        sys.argv += arglist
    main()
