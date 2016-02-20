
import io
import struct


from rxet.helper import unpack_uint32
from .bw_archive_base import BWArchiveBase, BWSection, BWResource


class ArchiveHeader(BWSection):
    def __init__(self, name, size, memview):
        assert name == b"RXET"
        strlength = unpack_uint32(memview, offset=0)
        offset = 4 + strlength

        super().__init__(name, size, memview, section_offset=offset)

        self.filename = self._header[4:4+strlength]

    def pack(self):
        # If the filename changed size, we have to resize the header
        if len(self.filename) != len(self._header) - 4:
            data = io.BytesIO()
            data.write(struct.pack("I", len(self.filename)))
            data.write(self.filename)
            self._header = data.getvalue()

            data.close()
        else:

            self._header[4:4+len(self.filename)] = self.filename

        return super().pack()


class TextureSection(BWSection):
    def __init__(self, name, size, memview):
        assert name == b"FTBX"
        super().__init__(name, size, memview, section_offset=4)

    def pack(self):
        texture_count = len(self.entries)

        self._header[0:4] = struct.pack("I", texture_count)

        return super().pack()


class TextureEntry(BWSection):
    def __init__(self, name, size, memview):
        assert name == b"TXET"

        super().__init__(name, size, memview, section_offset=0x54)

        self.tex_name = self._header[0x00:0x10]
        self.width = unpack_uint32(self._header, 0x10)
        self.height = unpack_uint32(self._header, 0x14)

        self.unknown1 = unpack_uint32(self._header, 0x18)
        self.unknown2 = unpack_uint32(self._header, 0x1C)

        self.tex_type = self._header[0x20:0x28]
        self.draw_type = self._header[0x28:0x30] # draw type is usually A8R8G8B8 in BW1

        self.unknowns = [unpack_uint32(self._header, 0x30+i*4) for i in range(8)]

    def pack(self):
        self._header[0x00:0x10] = bytes(self.tex_name).ljust(16, b"\x00")

        self._header[0x10:0x20] = struct.pack(
            "I"*4, self.width, self.height, self.unknown1, self.unknown2
        )

        self._header[0x20:0x28] = bytes(self.tex_type).ljust(8, b"\x00")
        self._header[0x28:0x30] = bytes(self.draw_type).ljust(8, b"\x00")

        self._header[0x30:0x50] = struct.pack("I"*8, *self.unknowns)
        #print(self.image_sections, len(self.entries), bytes(self.tex_type), bytes(self.draw_type))

        # P8 is a image format with a palette, so the amount of image entries is the amount of entries minus 1
        # due to one of the entries being the palette data (LAP), which doesn't count as an image.
        if self.tex_type == b"P8" + b"\x00"*6:
            image_sections = len(self.entries) - 1
        else:
            image_sections = len(self.entries)

        self._header[0x50:0x54] = struct.pack("I", image_sections)
        return super().pack()

    def get_format(self):
        return bytes(self.tex_type).rstrip(b"\x00")


class SoundSection(BWSection):
    def __init__(self, name, size, memview):
        assert name == b"DNOS"
        strlength = unpack_uint32(memview, offset=0)
        offset = 4 + strlength

        super().__init__(name, size, memview, section_offset=offset)

        self.filename = self._header[4:4+strlength]

    def pack(self):
        # If the filename changed size, we have to resize the header
        if len(self.filename) != len(self._header) - 4:
            data = io.BytesIO()
            data.write(struct.pack("I", len(self.filename)))
            data.write(self.filename)
            self._header = data.getvalue()

            data.close()
        else:

            self._header[4:4+len(self.filename)] = self.filename


        return super().pack()


class SoundCount(BWSection):
    def __init__(self, name, size, memview):
        assert name == b"HFSB"
        super().__init__(name, size, memview, section_offset=4)

        self.count = unpack_uint32(self._header, 0x00)

    def pack(self):
        self._header[0x00:0x04] = struct.pack("I", self.count)

        return super().pack()


class SoundName(BWSection):
    def __init__(self, name, size, memview):
        assert name == b"HPSD"
        super().__init__(name, size, memview, section_offset=0x20)

        self.modelname = self._header[0:0x20]

    def pack(self):
        self._header[0:0x20] = self.modelname

        return super().pack()




class BWArchive(BWArchiveBase):
    def __init__(self, f):
        super().__init__(f)

        # Unpack RXET into an object containing other resources
        assert self.entries[0].name == b"RXET"
        self.entries[0] = self.rxet = self.entries[0].as_section(cls=ArchiveHeader)
        assert len(self.rxet.entries) == 1

        assert self.rxet.entries[0].name == b"FTBX"
        self.rxet.entries[0] = self.ftb = self.rxet.entries[0].as_section(cls=TextureSection)

        for i in range(len(self.ftb.entries)):
            self.ftb.entries[i] = self.ftb.entries[i].as_section(cls=TextureEntry)

        assert self.entries[1].name == b"DNOS"
        self.entries[1] = self.dnos = self.entries[1].as_section(cls=SoundSection)

        assert self.dnos.entries[0].name == b"HFSB"
        self.dnos.entries[0] = self.hfsb = self.dnos.entries[0].as_section(cls=SoundCount)

        for i in range(1, len(self.dnos.entries)):
            assert self.dnos.entries[i].name in (b"HPSD", b"DPSD")

            if self.dnos.entries[i].name == b"HPSD":
                assert self.dnos.entries[i+1].name == b"DPSD"
                self.dnos.entries[i] = self.dnos.entries[i].as_section(cls=SoundName)

        self.sounds = [(self.dnos.entries[i], self.dnos.entries[i+1]) for i in range(1, len(self.dnos.entries), 2)]

        """for nameentry, dataentry in self.models:
            print(bytes(nameentry.modelname))
        print(self.dnos.entries[0].count)
        print((len(self.dnos.entries)-1)/2.0)"""

    def pack(self):
        # Adjust the amount of models in case models were taken away or added.
        # Every model has a HPSD entry and a DPSD entry in the DNOS section.
        self.hfsb.count = (len(self.dnos.entries) - 1) // 2

        return super().pack()

def get_rxet_size(header):
    return 4 + unpack_uint32(header, 0)

def get_ftb_size(header):
    return 4