from struct import unpack

from rxet.helper import read_uint32


def read_ftbx(fileobj):
    return fileobj.read(4), fileobj.read(4)


def read_txet(fileobj):
    dat = {}
    dat["unknown_int01"] = read_uint32(fileobj)
    dat["name_string"] = fileobj.read(16)
    dat["xsize"] = read_uint32(fileobj)
    dat["ysize"] = read_uint32(fileobj)
    dat["unknown_int04"] = read_uint32(fileobj)
    dat["unknown_flags"] = read_uint32(fileobj)

    nextBits = fileobj.read(4)
    # Extra data? Seems to be for TXET entries that aren't followed by a DXT1 entry
    if nextBits in (b"P8\x00\x00", b"A8R8"):
        dat["unknown_string"] = nextBits+fileobj.read(4)
        dat["unknown_ARGBstring"] = fileobj.read(8)

        dat["unknown_int05"] = read_uint32(fileobj)
        dat["unknown_int06"] = read_uint32(fileobj)
        dat["unknown_int07"] = read_uint32(fileobj)
        dat["unknown_int08"] = read_uint32(fileobj)
        dat["unknown_int09"] = read_uint32(fileobj)
        dat["unknown_int10"] = read_uint32(fileobj)
        dat["unknown_int11"] = read_uint32(fileobj)
        dat["unknown_int12"] = read_uint32(fileobj)

        dat["pim_count"] = read_uint32(fileobj)

    else:
        fileobj.seek(-4, 1)

    return dat


def read_dxt(fileobj):
    dat = {}
    dat["unknown_int1"] = fileobj.read(4)  # Only 0's?
    dat["unknown_ARGBstring"] = fileobj.read(8)
    #self.fileobj.read(2092)

    dat["unknown_int2"] = fileobj.read(4)  # Only 0's?
    dat["unknown_byte1"] = fileobj.read(1)  # always 0xFF?
    dat["unknown_int3_count"] = read_uint32(fileobj)  # A count for something?
    dat["unknown_int4_count"] = fileobj.read(4)

    dat["unknown_byte2"] = fileobj.read(1)  # Often 0x00, once 0x04? (in frontend_0_level.res)
    dat["unknown_short1"] = fileobj.read(2)  # Not sure if short

    dat["unknown_int5"] = fileobj.read(4)  # always 0xFF FF FF FF?

    dat["unknown_stuff"] = fileobj.read(16)  # Unknown data, mostly 0's? Fourth to last byte is 0x1?

    return dat


def read_pim(fileobj):
    dat = {}
    sectionsize = read_uint32(fileobj)
    #unknown_short1 = self.fileobj.read(2)

    dat["sectionsize"] = sectionsize
    dat["data"] = fileobj.read(sectionsize)

    #print "PIM Section, size: {0}".format(sectionsize)

    return dat


def read_lap(fileobj):
    dat = {}
    data_length = read_uint32(fileobj)
    #unknown_short = self.fileobj.read(2)
    dat["sectionsize"] = data_length
    dat["data"] = fileobj.read(data_length)

    return dat


def read_dnos(fileobj):
    dat = {}

    dat["unknown_int"] = fileobj.read(4)
    dat["string_length"] = read_uint32(fileobj)
    dat["name"] = fileobj.read(dat["string_length"])

    return dat


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
    dat = []
    length = read_uint32(fileobj)
    bin_data = fileobj.read(length)

    dat.append(length)
    dat.append(bin_data)
    return dat
"""
def read_ldom(self):
    dat = []
    dat.append(self.read_int())
    string_length = self.read_int()
    string = self.fileobj.read(string_length)

    dat.append(string_length)
    dat.append(string)

    return dat
"""