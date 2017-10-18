#!/usr/bin/env python
import argparse
import struct
from utils import escape_string
from cursor_proc import (PauseProc, AnimationProc, GoToProc, NextMsgProc,
                         SelectStringProc, ColorLineProc, ColorCharProc,
                         CharScaleProc, LineScaleProc, SoundTrigProc)

TABLE_ENT_STRUCT = struct.Struct('>I')

SPECIAL_CODES = {
    '\x00': 'LAST',
    '\x01': 'CONTINUE',
    '\x02': 'CLEAR',
    '\x03': PauseProc(),  # PAUSE (aka SetTime)
    '\x04': 'BUTTON',
    '\x05': ColorLineProc(),  # Color (whole line)
    '\x06': 'ABLE_CANCEL',  # 0x06: AbleCancel
    '\x07': 'UNABLE_CANCEL',  # 0x07: UnableCancel
    '\x08': AnimationProc(0),  # 0x08: SetDemoOrderPlayer
    '\x09': AnimationProc(1),  # 0x09: ANIMATION (aka SetDemoOrderNpc0)
    '\x0a': AnimationProc(2),  # 0x0A: SetDemoOrderNpc1
    '\x0b': AnimationProc(3),  # 0x0B: SetDemoOrderNpc2
    '\x0c': AnimationProc(4),  # 0x0C: SetDemoOrderNpc3
    '\x0d': 'SELECT_WINDOW',  # aka SetSelectWindow
    '\x0e': GoToProc(),  # 0x0e: GOTO_MESSAGE aka SetNextMessageF
    # 0x0f - 0x12 OPTIONS, aka SetNextMessage(0 through 3)
    '\x0f': NextMsgProc(0),
    '\x10': NextMsgProc(1),
    '\x11': NextMsgProc(2),
    '\x12': NextMsgProc(3),
    # 0x13 - 0x15: SetNextMessageRandom(2 through 4)
    # 0x16 - 0x18: SetSelectString(2 through 4)
    '\x16': SelectStringProc(2),
    '\x17': SelectStringProc(3),
    '\x18': SelectStringProc(4),
    '\x19': 'FORCE_NEXT',  # 0x19: SetForceNext
    '\x1a': 'PLAYER_NAME',
    '\x1b': 'TALK_NAME',
    '\x1c': 'PHRASE',  # aka "tail"
    '\x1d': 'YEAR',
    '\x1e': 'MONTH',
    '\x1f': 'WEEKDAY',
    '\x20': 'DAY',
    '\x21': 'HOUR',
    '\x22': 'MINUTE',
    '\x23': 'SECOND',
    # Free string inserts
    '\x24': 'FREE0',
    '\x25': 'FREE1',
    '\x26': 'FREE2',
    '\x27': 'FREE3',
    '\x28': 'FREE4',
    '\x29': 'FREE5',
    '\x2a': 'FREE6',
    '\x2b': 'FREE7',
    '\x2c': 'FREE8',
    '\x2d': 'FREE9',
    '\x2e': 'CHOICE',  # aka Determination (thing you just chose)
    '\x2f': 'TOWN',  # aka CountryName
    '\x30': 'RAND_NUM2',  # "RamdomNumber2"
    # Items (0x31 - 0x35)
    '\x31': 'ITEM0',
    '\x32': 'ITEM1',
    '\x33': 'ITEM2',
    '\x34': 'ITEM3',
    '\x35': 'ITEM4',
    # More free string inserts
    '\x36': 'FREE10',
    '\x37': 'FREE11',
    '\x38': 'FREE12',
    '\x39': 'FREE13',
    '\x3a': 'FREE14',
    '\x3b': 'FREE15',
    '\x3c': 'FREE16',
    '\x3d': 'FREE17',
    '\x3e': 'FREE18',
    '\x3f': 'FREE19',
    '\x40': 'MAIL0',
    # "Set Player Destiny" 0 - 9 (0x41 - 0x4A)
    '\x41': 'DESTINY0',
    '\x42': 'DESTINY1',
    '\x43': 'DESTINY2',
    '\x44': 'DESTINY3',
    '\x45': 'DESTINY4',
    '\x46': 'DESTINY5',
    '\x47': 'DESTINY6',
    '\x48': 'DESTINY7',
    '\x49': 'DESTINY8',
    '\x4a': 'DESTINY9',
    # Set Message Contents <emotion> (0x4B - 0x4F)
    '\x4b': 'NORMAL',
    '\x4c': 'ANGRY',
    '\x4d': 'SAD',
    '\x4e': 'FUN',
    '\x4f': 'SLEEPY',
    '\x50': ColorCharProc(),  # 0x50 COLOR aka SetColorChar
    '\x51': 'SOUND',
    '\x52': 'LINE_OFFSET',
    '\x53': 'LINE_TYPE',
    '\x54': CharScaleProc(),
    '\x55': 'BUTTON2',
    '\x56': 'BGM_MAKE',
    '\x57': 'BGM_DELETE',
    '\x58': 'MSG_TIME_END',
    '\x59': SoundTrigProc(),
    '\x5a': LineScaleProc(),
    '\x5b': 'SOUND_NO_PAGE',
    '\x5c': 'VOICE_TRUE',
    '\x5d': 'VOICE_FALSE',
    '\x5e': 'SELECT_NO_B',
    '\x5f': 'GIVE_OPEN',
    '\x60': 'GIVE_CLOSE',
    '\x61': 'GLOOMY',  # SetMessageContentsGloomy
    '\x62': 'SELECT_NO_B_CLOSE',
    '\x63': 'NEXT_MSG_RANDOM_SECTION',
    '\x64': 'AGB_DUMMY1',
    '\x65': 'AGB_DUMMY2',
    '\x66': 'AGB_DUMMY3',
    '\x67': 'SPACE',
    '\x68': 'AGB_DUMMY4',
    '\x69': 'AGB_DUMMY5',
    '\x6a': 'GENDER_CHECK',
    '\x6b': 'AGB_DUMMY6',
    '\x6c': 'AGB_DUMMY7',
    '\x6d': 'AGB_DUMMY8',
    '\x6e': 'AGB_DUMMY9',
    '\x6f': 'AGB_DUMMY10',
    '\x70': 'AGB_DUMMY11',
    '\x71': 'ISLAND_NAME',
    '\x72': 'SET_CURSOL_JUST',
    '\x73': 'CLR_CUSROL_JUST',
    '\x74': 'CUT_ARTICLE',
    '\x75': 'CAPITAL',
    '\x76': 'AMPM',
    '\x77': NextMsgProc(4),
    '\x78': NextMsgProc(5),
    '\x79': SelectStringProc(5),
    '\x7a': SelectStringProc(6),
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

                # Check for instance of processor
                if type(special) is not str:
                    proc = special
                    special = proc.process(message[i+2:])
                    special_len += proc.size()

            message = '%s[%s]%s' % (message[:i],
                                    special,
                                    message[i+special_len:])

            # Adjust message length and position
            msg_len = len(message)
            i += len(special) + 2
            continue

        i += 1

    message = escape_string(message)

    return message


def get_entries(data, table):
    '''Return array of (addr, entry) from data file and table file'''

    # The table is more like a table of ending positions, so we start
    # with an implicit entry at position 0
    entries = [0]

    pos = 0
    while pos < len(table):
        start = TABLE_ENT_STRUCT.unpack_from(table, offset=pos)[0]
        pos += TABLE_ENT_STRUCT.size

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
        print '#0x%04x @ 0x%08x (0x%02x bytes):' % (index, start, len(message))
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
    parser.add_argument('--table', type=str)
    parser.add_argument('--editor', action='store_true')
    parser.add_argument('--output', type=str, help='base of output filenames')
    args = parser.parse_args()

    dataf = open(args.data, 'rb')
    data = dataf.read()
    dataf.close()

    if args.table is not None:
        table_filename = args.table
    else:
        table_filename = args.data.replace('_data.bin', '_data_table.bin')

    tablef = open(table_filename, 'rb')
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

            table_bytes = TABLE_ENT_STRUCT.pack(cur_pos)

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
                table_pos += TABLE_ENT_STRUCT.size

            data_out_file.write(message)

        data_out_file.close()

        # Table zero padding
        table_pad_amount = len(table) - table_pos
        table_padding = '\x00' * (table_pad_amount)
        print 'padding table with %u bytes' % (table_pad_amount)

        table_out_file.write(table_padding)
        table_out_file.close()
    else:
        list_entries(entries)


if __name__ == '__main__':
    main()
