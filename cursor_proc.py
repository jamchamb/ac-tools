import struct


class CursorProc:

    def __init__(self):
        self._struct = struct.Struct(self.struct_format)
        self._size = self._struct.size

    def unpack(self, msg_buffer):
        return self._struct.unpack_from(msg_buffer)

    def process(self, msg_buffer):
        data = self.output_format % (self.unpack(msg_buffer))
        return '%s:%s' % (self.name, data)

    def size(self):
        return 2 + self._size


class PauseProc(CursorProc):

    name = 'PAUSE'
    struct_format = '>B'
    output_format = '0x%02x'


class AnimationProc(CursorProc):
    '''SetDemoOrderNpc0'''

    name = 'ANIM'
    struct_format = '>L'
    output_format = '0x%02x'

    def __init__(self):
        CursorProc.__init__(self)
        # Only 3 bytes are used to pack the int
        self._size = 3

    def unpack(self, msg_buffer):
        return self._struct.unpack_from('\x00' + msg_buffer[:self._size])


class GoToProc(CursorProc):
    '''SetNextMessageF'''

    name = 'GOTO'
    struct_format = '>H'
    output_format = '0x%04x'


class NextMsgProc(CursorProc):
    '''SetNextMessage(0-3)'''

    struct_format = '>H'
    output_format = '0x%04x'

    def __init__(self, num):
        CursorProc.__init__(self)
        self.name = 'OPT%u' % (num)


class SelectStringProc(CursorProc):
    '''SetSelectString(2-4)'''

    def __init__(self, num):

        self.name = 'SELECT%u' % (num)
        self.struct_format = '>' + ('H' * num)
        self.output_format = ','.join(['%04x' for _ in range(num)])

        CursorProc.__init__(self)


class ColorLineProc(CursorProc):

    name = 'COLOR'
    struct_format = '>I'
    output_format = '%06x'

    def __init__(self):
        CursorProc.__init__(self)
        self._size = 3

    def unpack(self, msg_buffer):
        return self._struct.unpack_from('\x00' + msg_buffer[:self._size])


class ColorCharProc(CursorProc):

    name = 'COLOR'
    struct_format = '>IB'
    output_format = '%06x:%02x'

    def __init__(self):
        CursorProc.__init__(self)
        self._size = 4

    def unpack(self, msg_buffer):
        return self._struct.unpack_from('\x00' + msg_buffer[:self._size])
