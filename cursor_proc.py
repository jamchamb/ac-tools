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
        return self._size


class PauseProc(CursorProc):

    name = 'PAUSE'
    struct_format = '>B'
    output_format = '0x%02x'


class AnimationProc(CursorProc):
    '''SetDemoOrder(Player,Npc(0-3))'''

    name = 'ANIM'
    struct_format = '>L'
    output_format = '0x%02x'

    anim_table = {
        0x01: 'SHOCK1',
        0x02: 'SURPRISE_HALO',
        0x03: 'LAUGH',
        0x04: 'SURPRISE_LINES',
        0x05: 'ANGRY_STEAM',
        0x06: 'SURPRISE_BANG',
        0x07: 'IMPATIENT',
        0x08: 'SHIVER',
        0x09: 'TEARS',
        0x0A: 'HAPPY_FLOWERS',
        0x0B: 'QUESTION',
        0x0C: 'IDEA_BULB',
        0x0D: 'GUST',
        0x0E: 'GIDDY',
        0x0F: 'THINK',
        0x10: 'RAIN_CLOUD',
        0x11: 'HEARTBREAK',
        0x12: 'WARUDAKUMI',
        0x13: 'SNORE',
        0x14: 'HEART',
        0x15: 'HAPPY_BROWS',
        0x16: 'ANGRY_BROWS',
        0x17: 'WORRY_BROWS',
        0xFF: 'DEFAULT'
    }

    def __init__(self, target):
        CursorProc.__init__(self)
        # Only 3 bytes are used to pack the int
        self._size = 3

        if target == 0:
            self.name += ':PLYR'
        else:
            self.name += ':NPC%u' % (target - 1)

    def unpack(self, msg_buffer):
        return self._struct.unpack_from('\x00' + msg_buffer[:self._size])

    def process(self, msg_buffer):
        anim_id = self.unpack(msg_buffer)[0]
        if anim_id in self.anim_table:
            description = self.anim_table[anim_id]
            return '%s:%s' % (self.name, description)
        else:
            return CursorProc.process(self, msg_buffer)


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


class CharScaleProc(CursorProc):

    name = 'CHAR_SCALE'
    struct_format = '>B'
    output_format = '0x%02x'


class LineScaleProc(CursorProc):

    name = 'LINE_SCALE'
    struct_format = '>B'
    output_format = '0x%02x'


class SoundTrigProc(CursorProc):

    name = 'SOUND_TRG_SYS'
    struct_format = '>B'
    output_format = '0x%02x'
