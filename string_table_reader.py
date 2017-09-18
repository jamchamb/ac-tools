#!/usr/bin/env python
import argparse
import struct
from utils import escape_string

TABLE_ENT_SZ = 4


SPECIAL_CODES = {
    '\x00': 'CLOSE',
    '\x01': 'END',
    '\x02': 'NEXT_PAGE',
    # 0x03: PAUSE
    '\x04': 'CONTINUE',
    # 0x09: ANIMATION
    '\x0d': '0x0D',
    # 0x0e: GOTO_MESSAGE
    # 0x0f - 0x12 OPTIONS

    '\x27': 'ACRE-LTR',
    '\x28': 'MEMSLOT/ACRE-NUM',
    '\x29': 'TARGET_NPC',

    '\x2e': 'CHOICE',

    '\x1a': 'PLAYER_NAME1',
    '\x1c': 'PHRASE',

    '\x1d': 'YEAR',
    '\x1e': 'MONTH',
    '\x1f': 'WEEKDAY',
    '\x20': 'DAY',
    '\x21': 'HOUR',
    '\x22': 'MINUTE',
    '\x23': 'SECOND',
    '\x76': 'AMPM',

    # also used for # of bells, could be generic variable insert
    '\x24': 'PLAYER_NAME2',
    '\x25': 'NPC_NAME',
    '\x2f': 'TOWN',
    '\x3a': 'NPC_TOWN',
    '\x3b': 'PLAYER_TOWN',

    #0x50 COLOR
    '\x5b': 'SHOW_SPECIAL',
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
                anim = struct.unpack('>L', '\x00'+message[i+2:i+2+3])[0]
                special = 'ANIM:0x%02x' % (anim)

            # GOTO
            elif special == '\x0e':
                special_len = 4
                target = struct.unpack('>H', message[i+2:i+2+2])[0]
                special = 'GOTO:0x%04x' % (target)

            # OPTION TRANSITIONS
            elif ord(special) >= 0x0f and ord(special) <= 0x12:
                special_len = 4
                index = ord(special) - 0x0f + 1
                target = struct.unpack('>H', message[i+2:i+2+2])[0]
                special = 'OPT%u:0x%04x' % (index, target)

            # CHOICES
            elif ord(special) >= 0x16 and ord(special) <= 0x18:
                count = ord(special) - 0x14

                special_len = 2 + (2 * count)
                choices = struct.unpack('>' + 'H'*count, message[i+2:i+2+(2 * count)])
                special = 'CHOICES:'
                for choice in choices:
                    special += '%04x,' % (choice)

            # COLOR (WHOLE LINE)
            elif special == '\x05':
                special_len = 5
                color = struct.unpack('>I', '\x00'+message[i+2:i+2+3])[0]
                special = 'COLOR:%06x' % (color)

            # COLOR (LENGTH)
            elif special == '\x50':
                special_len = 6
                color = struct.unpack('>I', '\x00'+message[i+2:i+2+3])[0]
                length =  struct.unpack('>B', message[i+2+3])[0]
                special = 'COLOR:%06x:%02x' % (color, length)

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

    index = 0
    for start, message in entries:
        print '#0x%04x @ 0x%08x:' % (index, start)
        print '%s\n' % (decode_message(message))
        index += 1


if __name__ == '__main__':
    main()
