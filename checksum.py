#!/usr/bin/env python
import argparse
import struct

COMMON_DATA_BASE = 0x26040
COMMON_DATA_SZ = 0x26000
CK_OFFSET = 0x12


def U16(x):
    return x & 0xFFFF


def update_checksum(gci_file):
    gci_file.seek(COMMON_DATA_BASE)

    checksum = 0
    for i in range(0, COMMON_DATA_SZ, 2):
        next_bytes = gci_file.read(2)
        if len(next_bytes) != 2:
            raise Exception("Expected 2 bytes at offset 0x%u, got %u" % (
                gci_file.tell(), len(next_bytes)))

        # Skip over existing checksum
        if i == CK_OFFSET:
            continue

        short = struct.unpack('>H', next_bytes)[0]
        checksum = U16(checksum + short)

    checksum = U16((2**16) - checksum)

    gci_file.seek(COMMON_DATA_BASE + CK_OFFSET)
    gci_file.write(struct.pack('>H', checksum))
    print 'Updated checksum: 0x%04x' % (checksum)


def main():
    parser = argparse.ArgumentParser(
        description='Update Animal Crossing save GCI checksum')
    parser.add_argument('gci_file', type=str)
    args = parser.parse_args()

    gci_file = open(args.gci_file, 'r+b')
    update_checksum(gci_file)
    gci_file.close()


if __name__ == '__main__':
    main()
