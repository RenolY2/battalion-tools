import os
from struct import pack, unpack
from PIL import Image

from bw_read_xml import BattWarsLevel
from bw_archive.bw_archive_base import BWArchiveBase
from rxet.helper import read_uint32

def decode_rgb565(color_val):
    b = (color_val & 0b11111) * (256//32)
    g = ((color_val >> 5) & 0b111111) * (256//64)
    r = ((color_val >> 11) & 0b11111) * (256//32)
    return r, g, b, 255


def read_section(f):
    id = f.read(4)
    size = read_uint32(f)
    data = f.read(size)

    return id, size, data


class RretFile(object):
    def __init__(self):
        self.sections = []
        self.size = None
        self.section_map = {}

    def parse(self, f):
        f.seek(-1, 2)
        size = f.tell()
        f.seek(0)

        while f.tell() < size:
            section = read_section(f)
            self.sections.append(section)
            self.section_map[section[0]] = section

    def write(self, f):
        for section in self.sections:
            id, size, data = section
            assert size == len(data)

            f.write(id)
            f.write(pack("I", size))
            f.write(data)


if __name__ == "__main__":
    #input_filepath = os.path.join("bw2_sandbox", "SP_1.1.pf2")
    in_dir = "BattalionWars/BW1/Data/CompoundFiles"
    files = os.listdir(in_dir)

    common_values = {}

    for filename in files:
        if not filename.endswith(".out"):
            continue

        in_path = os.path.join(in_dir, filename)

        with open(in_path, "rb") as f:
            #rret = RretFile()
            #rret.parse(f)
            out_data = BWArchiveBase(f)
        #print([(x[0],x[1]) for x in rret.sections])
        print([(entr.name, len(entr.data)) for entr in out_data.entries])

        assert out_data.entries[3].name == b"PAMC"
        pamc = out_data.entries[3]
        #id, size, data = rret.section_map[b"PAMC"]
        data = pamc.data

        pic = Image.new("RGBA", (64, 64))
        pix = pic.load()
        """
        pic2 = Image.new("RGBA", (64, 64))
        pix2 = pic2.load()"""

        #pic3 = Image.new("RGBA", (512, 512))
        #pix3 = pic3.load()

        #for x in range(128):
        #    for y in range(128):
        print(filename)
        for i in range(0, len(data)//4):
            x = (i) % 64
            y = (i) // 64
            """if x < 32:
                x *= 2
            else:
                x = x - 32
                x *= 2
                x += 1"""
            #index = y*128 + x
            #print(i)
            entry = data[i*4: (i+1)*4]

            entry_data = bytes(entry)

            r = g = b = 0
            a = 255

            unused, u, terrain_tile = unpack(">BBH", entry)

            if entry_data not in common_values:
                common_values[entry_data] = True
            #r = terrain_tile >> 8
            #g = terrain_tile & 0xFF
            g = u*64 #int(terrain_tile * (255.0/(2**10)))
            #if entry[3] >0:#< 255:
            #    entry[3] -= 1

            #entry[1] = 1
            #entry[2] = 0
            #entry[3] = 1
            #print("woohoo", r, g, b)
            #if col1 == 0xFF0F and i == 0:
            #    pix_[x,511-y] = r, g, b, 0
            #else:
            #print(x, y)
            if y > 63:
                print(x,y)
            else:
                pix[x,63-y] = r, g, b, a


        out = os.path.join("out", "BW1", filename+".png")
        #out2 = os.path.join("out", "BW1", filename+"2.png")
        #out3 = os.path.join("out", filename+"3.png")

        pic.save(out, "PNG")
        #pic2.save(out2, "PNG")
        #pic3.save(out3, "PNG")

        pic2 = Image.new("RGBA", (45, 64))
        pix2 = pic2.load()
        tcwu = out_data.entries[4]

        out_fixed = os.path.join("out", "BW1", filename)
        with open(out_fixed, "wb") as f:
            out_data.write(f)

    """
    with open("common_values.txt", "w") as f:
        f.write("")

    with open("common_values.txt", "a") as f:
        keys = [k for k in common_values.keys()]
        keys.sort()

        for key in keys:
            f.write("0x")
            for char in key:
                tmp = str(hex(char))[2:]
                f.write(tmp.rjust(2, "0"))
                f.write(" ")

            f.write("\n")"""

