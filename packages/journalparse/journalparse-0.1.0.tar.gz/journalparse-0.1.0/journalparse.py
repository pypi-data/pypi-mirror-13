import itertools
import struct


class State(object):
    FieldKey, TextFieldValue, BinaryFieldSize, BinaryFieldValue = range(4)


def bytes_in_file(fp):
    while True:
        byte = fp.read(1)
        if byte == b'':
            break
        yield byte


def journalparse(fp_or_iterable):
    state = State.FieldKey
    entry = {}
    buf = bytearray()

    if hasattr(fp_or_iterable, "read"):
        fp_or_iterable = bytes_in_file(fp_or_iterable)

    for byte in itertools.chain(fp_or_iterable, b"\n\n"):
        if not isinstance(byte, int):
            byte = ord(byte)
        if state == State.FieldKey:
            if byte == ord(b"="):
                key = buf
                state = State.TextFieldValue
                buf = bytearray()
            elif byte == ord(b"\n"):
                if buf:
                    key = buf
                    state = State.BinaryFieldSize
                else:
                    if entry:
                        yield entry
                        entry = {}
                buf = bytearray()
            else:
                buf.append(byte)
        elif state == State.TextFieldValue:
            if byte == ord(b"\n"):
                entry[key.decode("utf-8")] = buf.decode("utf-8")
                state = State.FieldKey
                buf = bytearray()
            else:
                buf.append(byte)
        elif state == State.BinaryFieldSize:
            if len(buf) < 8:
                buf.append(byte)
            if len(buf) == 8:
                size = struct.unpack("<Q", buf)[0]
                state = State.BinaryFieldValue
                buf = bytearray()
        elif state == State.BinaryFieldValue:
            if len(buf) < size:
                buf.append(byte)
            elif byte == ord(b"\n"):
                entry[key.decode("utf-8")] = buf
                state = State.FieldKey
                buf = bytearray()
            else:
                raise Exception("Expected end of data (newline) after %d bytes, got %s instead" % (size, repr(byte)))
        else:
            raise Exception("Unexpected state: %s" % state)

