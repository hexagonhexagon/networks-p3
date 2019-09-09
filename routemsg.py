"""routemsg.py: construct and deconstruct router messages.
"""
import pickle

def make_routemsg(is_link, srcname, srcport, data):
    """Create router message with following format:
    +-----+------+--------------------+
    | src | srcn | source router port |
    +-----+------+--------------------+
    | data....                        |
    +---------------------------------+
    src: 1 byte, 0x00=router source, 0xFF=link source
    srcn: 1 byte, destination name (1 character)
    source router port: 2 bytes
    data: variable length
    """
    packet = bytearray(b'')
    port_bytes = srcport.to_bytes(2, byteorder='big', signed=False)
    data_bytes = pickle.dumps(data)
    
    if is_link:
        packet.append(255)
    else:
        packet.append(0)
    packet.append(ord(srcname))
    for i in range(2):
        packet.append(port_bytes[i])
    for i in range(len(data_bytes)):
        packet.append(data_bytes[i])

    return packet
    
def get_routemsg(packet):
    """Deconstruct router message and return a 4-tuple:
    (is_link, srcname, srcport, data)
    """

    is_link_byte = packet[0]
    is_link = False
    if is_link_byte:
        is_link = True
    srcname = chr(packet[1])
    srcport = int.from_bytes(packet[2:4], byteorder='big', signed=False)
    data = pickle.loads(packet[4:])

    return is_link, srcname, srcport, data
    
