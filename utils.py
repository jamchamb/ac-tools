import string

def escape_string(msg):
    i = 0
    msg_len = len(msg)

    while i < msg_len:
        if msg[i] not in string.printable:
            escaped = '\\x%02x' % (ord(msg[i]))
            msg = '%s%s%s' % (msg[:i], escaped, msg[i+1:])
            msg_len += 3
            i += 4
            continue
        i += 1

    return msg
