#!/usr/bin/env python
import argparse
import struct
from utils import escape_string

TABLE_ENT_SZ = 4


SPECIAL_CODES = {
    '\x02': 'NEXT_PAGE',
    #0x03: PAUSE
    '\x04': 'CONTINUE',
    #0x09: ANIMATION

    '\x28': 'MEMSLOT',

    '\x1c': 'NICKNAME',

    '\x1d': 'YEAR',
    '\x1e': 'MONTH',
    '\x1f': 'WEEKDAY',
    '\x20': 'DAY',
    '\x21': 'HOUR',
    '\x22': 'MINUTE',
    '\x23': 'SECOND',
    '\x76': 'AMPM',

    '\x24': 'PLAYER_NAME',
    '\x25': 'NPC_NAME',
    '\x2f': 'TOWN',
    '\x3a': 'NPC_TOWN',
    '\x3b': 'PLAYER_TOWN',

    #0x50 COLOR
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
            special_len = 2

            if special in SPECIAL_CODES:
                special = SPECIAL_CODES[special]

            # PAUSE
            elif special == '\x03':
                special = 'PAUSE:0x%02x' % (ord(message[i+1]))
                special_len = 3

            # ANIMATION
            elif special == '\x09':
                special_len = 5
                anim = struct.unpack('>I', message[i+1:i+1+4])[0] - 0x09000000
                special = 'ANIM:0x%02x' % (anim)

            # COLOR
            elif special == '\x50':
                special_len = 6
                color = struct.unpack('>I', '\x00'+message[i+2:i+2+3])[0]
                special = 'COLOR:%06x:%02x' % (color, struct.unpack('>B', message[i+2+3])[0])

            message = '%s[%s]%s' % (message[:i], special, message[i+special_len:])

            # Adjust message length and position
            msg_len = len(message)
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
