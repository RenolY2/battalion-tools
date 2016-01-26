import warnings

from struct import unpack
from rxet.parsers_bw1 import (
    read_dnos, read_dpsd, read_dxt,
    read_ftbx,read_hfsb, read_hpsd,
    read_lap, read_pim, read_txet
)

class RXET():
    def __init__(self, fileobj, version):
        self.fileobj = fileobj

        if version == "BW1":
            self.parser = {b"FTBX": read_ftbx,
                           b"TXET": read_txet,
                           b"DXT1": read_dxt,
                           b" PIM": read_pim,
                           b" LAP": read_lap,
                           b"DNOS": read_dnos,
                           b"HFSB": read_hfsb,
                           b"HPSD": read_hpsd,
                           b"DPSD": read_dpsd}
                           #b"LDOM": self.read_ldom}
        elif version == "BW2":
            pass
        else:
            raise RuntimeError("Unknown version: {0}".format(version))

    def parse_rxet(self, strict=True, verbose=False):
        size = 0
        self.fileobj.seek(-1, 2)
        size = self.fileobj.tell()
        self.fileobj.seek(0)

        data = []
        header = self.fileobj.read(4)
        unknown_int = self.fileobj.read(4)
        
        filename_length =  unpack("I", self.fileobj.read(4))[0]
        filename = self.fileobj.read(filename_length)

        misc = (header, unknown_int, filename_length, filename)

        if verbose:
            print(misc)

        while self.fileobj.tell() < size:
            section_name = self.fileobj.read(4)
            if verbose:
                print(section_name, hex(self.fileobj.tell()), len(section_name))

            if section_name in self.parser:
                start = self.fileobj.tell()
                sectionData = self.parser[section_name](self.fileobj)
                data.append((section_name, start, self.fileobj.tell(), sectionData))
            else:
                trouble_offset = self.fileobj.tell()
                if strict:
                    raise RuntimeError("Unknown section: {0}\nCurrent position offset: {1}"
                                       "".format(section_name, hex(trouble_offset) ))
                else:
                    warnings.warn("Unknown section: {0}\nCurrent position offset: {1}"
                                  "".format(section_name, hex(trouble_offset)))
                    break

            
        #print unpack("H", unknown_short2)
        return misc, data


if __name__ == "__main__":
    #filename = "frontend_0_Level.res"
    import os
    import string
    ALPHAWHITESPACE = bytes(string.ascii_uppercase+" ", encoding="ascii")
    import json
    
    dir = "BattalionWars/BW1/Data/CompoundFiles"
    files = os.listdir(dir)

    outdir = "out/"
    
    txet_data = {}
    
    for filename in files:
        if not filename.endswith(".res"):
            continue

        txet_data[filename] = []
        entities = []
        path = os.path.join(dir, filename)

        print(filename)
        print(all((x in ALPHAWHITESPACE for x in ALPHAWHITESPACE)))
        with open(path, "rb") as inputfile:
            try:
                rxet = RXET(inputfile, "BW1")
                misc, data = rxet.parse_rxet(strict=False)
            except RuntimeError:
                print(hex(rxet.fileobj.tell()))
                curr = rxet.fileobj.tell()

                hits = 0

                while True:
                    string = rxet.fileobj.read(4)
                    if all(char in ALPHAWHITESPACE for char in string):
                        print("next possible spot:", string, hex(rxet.fileobj.tell()))
                        hits += 1

                    rxet.fileobj.seek(-3, 1)

                    if hits > 15:
                        break
                rxet.fileobj.seek(curr)
                raise


        out_path = os.path.join(outdir, filename+".txt")
        with open(out_path, "w") as f:
            f.write("")



        with open(out_path, "a") as f:
            f.write("=\n=")
            f.write(str(misc))
            f.write("\n=\n")
            for entry in data:
                section_name, start, end, section_data = entry
                f.write("{0} start: {1} end: {2}, size: {3}".format(section_name, start, end, end-start))
                if section_name in (b"FTBX", b"TXET", b"DXT1"):
                    f.write(": ")
                    f.write(str(section_data))
                f.write("\n")

        #txet_data[filename].insert(0, entities)
