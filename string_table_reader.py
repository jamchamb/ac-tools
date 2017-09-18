#!/usr/bin/env python
import argparse
import struct
from utils import escape_string

TABLE_ENT_SZ = 4


SPECIAL_CODES = {
    '$': 'PLAYER_NAME',
    ';': 'PLAYER_TOWN',
    '%': 'NPC_NAME',
    ':': 'NPC_TOWN',
}


def decode_message(message):
    '''Translate special values in an AC message'''

    # 0xCD: newline
    message = message.replace('\xcd', '\n')

    msg_len = len(message)
    i = 0
    while i < msg_len:
        # Check for special meta-chars
        if message[i] == '\x7f':
            special = message[i+1]
            if special in SPECIAL_CODES:
                special = SPECIAL_CODES[special]

            message = '%s[%s]%s' % (message[:i], special, message[i+2:])

            # Adjust message length and position
            msg_len += len(special)
            i += len(special) + 2
            continue

        i += 1

    message = escape_string(message)

    return message


def get_entries(data, table):
    entries = [0]

    index = 0
    pos = 0
    while pos < len(table):
        start = struct.unpack('>I', table[pos:pos+TABLE_ENT_SZ])[0]
        pos += TABLE_ENT_SZ
        index += 1

        if start == 0:
            break

        entries.append(start)

    for i in range(len(entries)):
        if i == len(entries) - 1:
            end = len(data)
        else:
            end = entries[i+1]

        start = entries[i]
        message = data[start:end]
        entries[i] = (start, message)

    return entries


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('data', type=str)
    parser.add_argument('table', type=str)
    args = parser.parse_args()

    dataf = open(args.data, 'rb')
    data = dataf.read()
    dataf.close()

    tablef = open(args.table, 'rb')
    table = tablef.read()
    tablef.close()

    entries = get_entries(data, table)

    for start, message in entries:
        print '0x%08x:' % (start)
        print '%s\n' % (decode_message(message))


if __name__ == '__main__':
    main()
