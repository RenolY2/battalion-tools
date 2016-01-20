from struct import unpack

class RXET():
    def __init__(self, fileobj):
        self.fileobj = fileobj
        self.parser = {b"FTBX": self.read_ftbx,
                       b"TXET": self.read_txet,
                       b"DXT1": self.read_dxt,
                       b" PIM": self.read_pim,
                       #"P8\x00\x00" : self.read_TXET_P8,
                       b" LAP": self.read_lap,
                       b"DNOS": self.read_dnos,
                       b"HFSB": self.read_hfsb,
                       b"HPSD": self.read_hpsd,
                       b"DPSD": self.read_dpsd,
                       b"LDOM": self.read_ldom}

    def read_int(self):
        return unpack("I", self.fileobj.read(4))[0]

    def parse_rxet(self):
        size = 0
        self.fileobj.seek(-1, 2)
        size = self.fileobj.tell()
        self.fileobj.seek(0)

        data = []
        header = self.fileobj.read(4)
        unknown_int = self.fileobj.read(4)#unpack("I", self.fileobj.read(4))[0]
        
        filename_length =  unpack("I", self.fileobj.read(4))[0]
        filename = self.fileobj.read(filename_length)

        misc = (header, unknown_int, filename_length, filename)
        print(misc)
        #for i in range(section_count):
        while self.fileobj.tell() < size:

            section_name = self.fileobj.read(4)
            print(section_name, hex(self.fileobj.tell()), len(section_name))
            if section_name in self.parser:
                start = self.fileobj.tell()
                sectionData = self.parser[section_name]()
                data.append((section_name, start, self.fileobj.tell(), sectionData))
                #if section_name == b"TXET":
                #    print(sectionData)
            else:
                trouble_offset = self.fileobj.tell()
                raise RuntimeError("Unknown section: {0}\nCurrent position offset: {1}"
                                   "".format(section_name, hex(trouble_offset) ))

            
        #print unpack("H", unknown_short2)
        return misc, data

    def read_ftbx(self):
        dat = {}
        dat["unknown_int1"] = self.fileobj.read(4)
        dat["unknown_int2"] = self.fileobj.read(4)
        
        return dat
    
    def read_txet(self):
        dat = {}
        dat["unknown_int01"] = unpack("I", self.fileobj.read(4))[0]
        dat["name_string"] = self.fileobj.read(16)
        dat["unknown_int02"] = unpack("I", self.fileobj.read(4))[0]
        dat["unknown_int03"] = unpack("I", self.fileobj.read(4))[0]
        dat["unknown_int04"] = unpack("I", self.fileobj.read(4))[0]
        dat["unknown_flags"] = unpack("I", self.fileobj.read(4))[0]
        
        nextBits = self.fileobj.read(4)
        # Extra data? Seems to be for TXET entries that aren't followed by a DXT1 entry
        if nextBits in (b"P8\x00\x00", b"A8R8"):
            dat["unknown_string"] = nextBits+self.fileobj.read(4)
            dat["unknown_ARGBstring"] = self.fileobj.read(8)
            
            dat["unknown_int05"] = unpack("I", self.fileobj.read(4))[0]
            dat["unknown_int06"] = unpack("I", self.fileobj.read(4))[0]
            dat["unknown_int07"] = unpack("I", self.fileobj.read(4))[0]
            dat["unknown_int08"] = unpack("I", self.fileobj.read(4))[0]
            dat["unknown_int09"] = unpack("I", self.fileobj.read(4))[0]
            dat["unknown_int10"] = unpack("I", self.fileobj.read(4))[0]
            dat["unknown_int11"] = unpack("I", self.fileobj.read(4))[0]
            dat["unknown_int12"] = unpack("I", self.fileobj.read(4))[0]


            dat["pim_count"] = unpack("I", self.fileobj.read(4))[0]
        else:
            self.fileobj.seek(-4, 1)
        
        return dat
        
    def read_dxt(self):
        dat = {}
        dat["unknown_int1"] = self.fileobj.read(4)  # Only 0's?
        dat["unknown_ARGBstring"] = self.fileobj.read(8)
        #self.fileobj.read(2092)
        
        dat["unknown_int2"] = self.fileobj.read(4)  # Only 0's?
        dat["unknown_byte1"] = self.fileobj.read(1)  # always 0xFF?
        dat["unknown_int3_count"] = unpack("I", self.fileobj.read(4))[0]  # A count for something?
        dat["unknown_int4_count"] = self.fileobj.read(4)
        
        dat["unknown_byte2"] = self.fileobj.read(1)  # Often 0x00, once 0x04? (in frontend_0_level.res)
        dat["unknown_short1"] = self.fileobj.read(2)  # Not sure if short
        
        dat["unknown_int5"] = self.fileobj.read(4)  # always 0xFF FF FF FF?
        
        dat["unknown_stuff"] = self.fileobj.read(16)  # Unknown data, mostly 0's? Fourth to last byte is 0x1?
        
        return dat
        
    def read_pim(self):
        dat = {}
        sectionsize = unpack("I",self.fileobj.read(4))[0]
        #unknown_short1 = self.fileobj.read(2)
        
        dat["sectionsize"] = sectionsize
        dat["data"] = self.fileobj.read(sectionsize) 
        
        #print "PIM Section, size: {0}".format(sectionsize)
        
        return dat
    
    def read_lap(self):
        dat = {}
        data_length = unpack("I", self.fileobj.read(4))[0]
        #unknown_short = self.fileobj.read(2)
        dat["sectionsize"] = data_length
        dat["data"] = self.fileobj.read(data_length)
        
        return dat

    def read_dnos(self):
        dat = {}

        dat["unknown_int"] = self.fileobj.read(4)
        dat["string_length"] = unpack("I", self.fileobj.read(4))[0]
        dat["name"] = self.fileobj.read(dat["string_length"])

        return dat

    def read_hfsb(self):
        dat = []
        dat.append(self.fileobj.read(4))
        dat.append(self.fileobj.read(4))

        return dat

    def read_hpsd(self):
        dat = []
        length = self.read_int()
        string = self.fileobj.read(length)
        dat.append(length)
        dat.append(string)

        return dat

    def read_dpsd(self):
        dat = []
        length = unpack("I", self.fileobj.read(4))[0]
        bin_data = self.fileobj.read(length)

        print(hex(length))

        dat.append(length)
        dat.append(bin_data)
        return dat

    def read_ldom(self):
        dat = []
        dat.append(self.read_int())
        string_length = self.read_int()
        string = self.fileobj.read(string_length)

        dat.append(string_length)
        dat.append(string)

        return dat


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
                rxet = RXET(inputfile)
                misc, data = rxet.parse_rxet()
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

        """
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
        """