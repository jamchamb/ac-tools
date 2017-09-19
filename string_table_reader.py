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

    if len(message) < 1:
        return message

    # Check for empty end entry
    if message[0] == '\x00':
        if len(set([c for c in message])) == 1:
            return '[%u FREE BYTES]' % (len(message))

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
    '''Return array of (addr, entry) from data file and table file'''
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


def list_entries(entries):
    index = 0
    for start, message in entries:
        print '#0x%04x @ 0x%08x:' % (index, start)
        print '%s\n' % (decode_message(message))
        index += 1


def edit_entries(entries):
    '''Edit string table'''

    prompt = 'choose entry 0x00 through 0x%04x (s <text> to search, q to quit): ' % \
             (len(entries))

    print prompt

    choice = None
    while True:
        if choice is not None:
            print prompt

        choice = raw_input()

        # handle search terms
        if len(choice) > 0 and choice[0] == 's':
            if choice[1] == ' ':
                terms = choice[2:]
            else:
                terms = choice[1:]

            for idx, entry in enumerate(entries):
                if terms.lower() in entry[1].lower():
                    print '#0x%04x: %s' % (idx, escape_string(entry[1][:20]))
            continue
        elif choice.lower() == 'q':
            break

        # handle index choice
        choice = int(choice, 16)
        if choice < 0 or choice > (len(entries) - 1):
            print 'invalid choice'
            continue

        message = entries[choice][1]

        print '#0x%04x: %s' % (choice, escape_string(message))
        print 'decoded:\n%s' % (decode_message(message))

        print 'new value:'
        new_entry = raw_input()
        print 'Changed to "%s"' % (new_entry)
        entries[choice] = (entries[choice][0], new_entry)

    return entries


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('data', type=str)
    parser.add_argument('table', type=str)
    parser.add_argument('--editor', action='store_true')
    parser.add_argument('--output', type=str, help='base of output filenames')
    args = parser.parse_args()

    dataf = open(args.data, 'rb')
    data = dataf.read()
    dataf.close()

    tablef = open(args.table, 'rb')
    table = tablef.read()
    tablef.close()

    entries = get_entries(data, table)

    if args.editor:
        edited_entries = edit_entries(entries)
        data_out_filename = args.output + '_data.bin'
        table_out_filename = args.output + '_data_table.bin'

        data_out_file = open(data_out_filename, 'wb')
        table_out_file = open(table_out_filename, 'wb')

        cur_pos = 0
        table_pos = 0

        for idx, entry in enumerate(edited_entries):
            message = entry[1]
            cur_pos += len(message)

            table_bytes = struct.pack('>I', cur_pos)

            # Handle zero pad entry at the end
            if idx == len(entries) - 1:
                orig_pad_len = len(message)

                orig_size = len(data)
                new_size = cur_pos
                size_diff = orig_size - new_size

                if size_diff > 0:
                    print 'adding %u bytes to data zero pad' % (size_diff)
                elif size_diff < 0:
                    print 'removing %u bytes from data zero pad' % (-size_diff)
                else:
                    print 'zero pad unchanged'

                new_pad_len = orig_pad_len + size_diff

                if new_pad_len < 0:
                    print 'Invalid padding length %d' % (new_pad_len)
                    break

                message = '\x00' * new_pad_len
            # Don't add a table entry after the zero pad
            else:
                table_out_file.write(table_bytes)
                table_pos += TABLE_ENT_SZ

            data_out_file.write(message)

        data_out_file.close()

        # TODO Zero padding
        table_pad_amount = len(table) - table_pos
        table_padding = '\x00' * (table_pad_amount)
        print 'padding table with %u bytes' % (table_pad_amount)
        table_out_file.write(table_padding)
        table_out_file.close()
    else:
        list_entries(entries)


if __name__ == '__main__':
    main()
