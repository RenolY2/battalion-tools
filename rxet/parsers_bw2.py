from rxet.helper import read_uint32, read_uint32_BE
from collections import namedtuple



DxtgData = namedtuple("DXTG", ["size", "name", "unk_int2", "unk_int3", "unk_int4", "unk_int5",
                               "image_type", "unk_int6", "unk_int7", "unk_int8", "unk_int9",
                               "unk_ints", "unk_int10", "size_x", "size_y", "unk_int13"])
LapData = namedtuple("LAP", ["size", "data"])
PimData = namedtuple("PIM", ["size", "data"])
DnosData = namedtuple("DNOS", ["unk_int", "strlength", "name"])
HpsdData = namedtuple("HPSD", ["length", "name"])
DpsdData = namedtuple("DPSD", ["length", "data"])

def read_ftbg(fileobj):
    return fileobj.read(4), fileobj.read(4)


def read_dxtg(fileobj):
    #dat = {}
    size = read_uint32(fileobj)
    name = fileobj.read(0x20).strip(b"\x00")
    unk_int2 = read_uint32_BE(fileobj)
    unk_int3 = read_uint32_BE(fileobj)
    unk_int4 = read_uint32_BE(fileobj)
    unk_int5 = read_uint32_BE(fileobj)
    image_type = fileobj.read(0x10).strip(b"\x00")
    unk_int6 = read_uint32_BE(fileobj)
    unk_int7 = read_uint32_BE(fileobj)
    unk_int8 = read_uint32_BE(fileobj)
    unk_int9 = read_uint32_BE(fileobj)
    unknown_ints = fileobj.read(0x10)
    unk_int10 = read_uint32_BE(fileobj)
    size_x = read_uint32_BE(fileobj)
    size_y = read_uint32_BE(fileobj)
    unk_int13 = read_uint32_BE(fileobj)

    return DxtgData(size, name, unk_int2, unk_int3, unk_int4, unk_int5,
                    image_type, unk_int6, unk_int7, unk_int8, unk_int9,
                    unknown_ints, unk_int10, size_x, size_y, unk_int13)


def read_pim(fileobj):
    data_length = read_uint32(fileobj)
    data = fileobj.read(data_length)

    return PimData(data_length, data)


def read_lap(fileobj):
    data_length = read_uint32(fileobj)
    data = fileobj.read(data_length)

    return LapData(data_length, data)


def read_dnos(fileobj):
    unk_int = fileobj.read(4)
    strlength = read_uint32(fileobj)
    name = fileobj.read(strlength)

    return DnosData(unk_int, strlength, name)


def read_hfsb(fileobj):
    return fileobj.read(4), fileobj.read(4)


def read_hpsd(fileobj):
    dat = []
    length = read_uint32(fileobj)
    string = fileobj.read(length)
    dat.append(length)
    dat.append(string)

    return dat


def read_dpsd(fileobj):
    length = read_uint32(fileobj)
    bin_data = fileobj.read(length)
    return DpsdData(length, bin_data)


def read_prcs(fileobj):
    length = read_uint32(fileobj)
    data = fileobj.read(length)
    return length, data


def read_feqt(fileobj):
    length = read_uint32(fileobj)
    data = fileobj.read(length)
    return length, data


def read_ldom(fileobj):
    length = read_uint32(fileobj)
    data = fileobj.read(length)
    return length, data