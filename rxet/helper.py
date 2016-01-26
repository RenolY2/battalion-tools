from struct import unpack


def read_uint32(fileobj):
    return unpack("I", fileobj.read(4))[0]