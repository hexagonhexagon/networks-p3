"""routerpr.py: Starts a router that uses poison reverse to minimize messages sent.
Usage: router <name> <port>: creates a router listening on <port> with name
<name>. <name> must be one character long.
"""

"""Since there are so many variables, here is a minor guide:

name: name of this router
port: port this router is operating on
srcname: name of router message was received from
srcport: port of router message was received from

neighbors[name][0]: port number of neighbor name
neighbors[name][1]: link cost to neighbor name

dist_vecs[src]: all distance vectors for src, equivalent to dist_vecs[src].keys() when iterating
dist_vecs[src][dest][0]: cost of path from src to dest
dist_vecs[src][dest][1]: # hops in path from src to dest
dist_vecs[src][dest][2]: next router in path from src to dest

An outline of the structure of neighbors and dist_vecs is also included."""

import socket
import sys
import logging
from time import sleep
from math import inf
from routemsg import *

prompt_for_args = False #set to true to prompt for command line args.

def print_distvecs(dvs, name):
    print('- - - - -')
    for dest in dvs[name].keys():
        if name != dest:
            print(name, dest, dvs[name][dest][0],
                  dvs[name][dest][1], dvs[name][dest][2])

def main():
    if len(sys.argv) == 1:
        print(__doc__)
    elif len(sys.argv) == 2:
        print('Need a port number!')
    elif len(sys.argv) == 3:
        if len(sys.argv[1]) != 1:
            print('Name must be a single character.')
        else:
            try:
                int(sys.argv[2])
            except ValueError:
                print('Port number must be an integer!')
                return

            logging.basicConfig(format='%(message)s  (%(levelname)s)', level=logging.CRITICAL)
            #change level=logging.DEBUG to display debug messages
            
            name = sys.argv[1]
            port = int(sys.argv[2])
            routerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                routerSocket.bind(('', port))
            except socket.error as e:
                print(e)
                return

            neighbors = {} #name:(port, cost)
            dist_vecs = {name:{name:(0, 0, name)}} #src:{dest:(cost, hops, next_router)}
            print('Router {} is active. Waiting for links to be added...'.format(name))
            
            while True:
                msg, srcaddr = routerSocket.recvfrom(1024)
                is_link, srcname, srcport, data = get_routemsg(msg)
                send_dv = False
                
                if is_link: #link msg
                    send_dv = True
                    neighbors[srcname] = (srcport, data) #overwrite neighbor info
                    if srcname not in dist_vecs: #no dv?
                        dist_vecs[srcname] = {}
                        dist_vecs[name][srcname] = (int(data), 1, srcname)
                    else: #have dv
                        pass
                            
                else:
                    waittime = .01 * neighbors[srcname][1]
                    sleep(waittime) #wait 10ms * link cost
                    dist_vecs[srcname] = data #replace old dvs
                    for dest in dist_vecs[srcname]:
                        if name == dest:
                            continue #if calculating dist to itself, skip

                        old_vec = (inf, inf, name)
                        if dest in dist_vecs[name]:
                            old_vec = dist_vecs[name][dest]
                        dist_vecs[name][dest] = (inf, inf, name) #overwrite old value/add new one
                                
                        for neighbor in neighbors:
                            logging.debug('%s to %s thru %s', name, dest, neighbor)
                            logging.debug('%s | %s | %s', neighbors[neighbor][1],
                                  dist_vecs[neighbor].get(dest, (inf,))[0],
                                  dist_vecs[name].get(dest, (inf,))[0])
                            logging.debug('%s to %s: %s. %s to %s: %s', neighbor, dest,
                                          dist_vecs[neighbor].get(dest, (0,0,'?'))[2], name, dest,
                                          dist_vecs[name].get(dest, (0,0,'?'))[2])
                            
                            if (neighbors[neighbor][1] + dist_vecs[neighbor].get(dest, (inf,))[0]
                                < dist_vecs[name].get(dest, (inf,))[0]):

                                dist_vecs[name][dest] = (neighbors[neighbor][1]
                                                        + dist_vecs[neighbor][dest][0],
                                                        dist_vecs[neighbor][dest][1] + 1, neighbor)
                        for neighbor in neighbors:    
                            if (dist_vecs[neighbor].get(dest, (0,0,'?'))[2] == name
                                and dist_vecs[name].get(dest, (0,0,'?'))[2] == neighbor): #poison reverse
                                print('Poison reverse!')
                                dist_vecs[name][dest] = (inf, inf, name)
                            
                        if dist_vecs[name][dest] != old_vec:
                            send_dv = True
                            logging.debug('%s, %s, %s', dist_vecs[name][dest], old_vec, send_dv)
                    """Bellman-Ford equation applied directly: dist_vecs[name][dest]
                    is the minimum of c(name, neighbor) + d(neighbor, dest).
                    Note that if the old value is not overwritten, an increase in link
                    cost will be ignored in the distance vectors."""
                    

                print_distvecs(dist_vecs, name) #modifications done, print
                logging.debug('%s', neighbors)

                if send_dv:
                    dv_msg = make_routemsg(False, name, port, dist_vecs[name])
                    for neighbor in neighbors:
                        routerSocket.sendto(dv_msg, ('127.0.0.1', neighbors[neighbor][0]))
                
    else:
        print('Too many arguments.')

if __name__ == '__main__':
    if prompt_for_args: 
        arglist = input('Enter command line args: ').split()
        sys.argv += arglist
    main()
