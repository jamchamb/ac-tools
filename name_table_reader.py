#!/usr/bin/env python
import argparse
import struct
from utils import escape_string


def get_entries(data):
    '''Return array of name entries'''
    entries = []

    for i in range(0, len(data), 8):
        entries.append(data[i:i+8])

    return entries


def list_entries(entries):
    for idx, name in enumerate(entries):
        print '%2u: %s' % (idx, name)


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
                if terms.lower() in entry.lower():
                    print '#0x%04x: %s' % (idx, escape_string(entry))
            continue
        elif choice.lower() == 'q':
            break

        # handle index choice
        choice = int(choice, 16)
        if choice < 0 or choice > (len(entries) - 1):
            print 'invalid choice'
            continue

        message = entries[choice]

        print '#0x%04x: %s' % (choice, escape_string(message))

        print 'new value:'
        new_entry = raw_input()

        if len(new_entry) < 8:
            new_entry += ' ' * (8 - len(new_entry))
        elif len(new_entry) > 8:
            print 'name may only be up to 8 characters'
            continue

        print 'Changed to "%s"' % (new_entry)
        entries[choice] = new_entry

    return entries


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('data', type=str)
    parser.add_argument('--editor', action='store_true')
    parser.add_argument('--output', type=str, help='base of output filenames')
    args = parser.parse_args()

    dataf = open(args.data, 'rb')
    data = dataf.read()
    dataf.close()

    entries = get_entries(data)

    if args.editor:
        edited_entries = edit_entries(entries)
        data_out_filename = args.output

        data_out_file = open(data_out_filename, 'wb')

        for name in edited_entries:
            if len(name) < 8:
                name += ' ' * (8 - len(name))
            elif len(name) > 8:
                raise Exception('name can only be up to 8 characters')

            data_out_file.write(name)
    else:
        list_entries(entries)


if __name__ == '__main__':
    main()
