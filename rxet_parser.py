from struct import unpack

class RXET():
    def __init__(self, fileobj):
        self.fileobj = fileobj
        self.parser = {b"FTBX": self.read_ftbx,
                       b"TXET": self.read_txet,
                       b"DXT1": self.read_dxt,
                       b" PIM": self.read_pim,
                       #"P8\x00\x00" : self.read_TXET_P8,
                       b" LAP": self.read_lap}

    def parse_rxet(self):
        data = []
        header = self.fileobj.read(4) 
        unknown_short1 = self.fileobj.read(2)
        section_count = unpack("H", self.fileobj.read(2))[0]
        
        filename_length =  unpack("I", self.fileobj.read(4))[0]
        filename = self.fileobj.read(filename_length)

        misc = (header, unknown_short1, section_count, filename_length, filename)
        
        for i in range(section_count):
            section_name = self.fileobj.read(4)
            #print(section_name, hex(self.fileobj.tell()), len(section_name))
            if section_name in self.parser:
                start = self.fileobj.tell()
                sectionData = self.parser[section_name]()
                data.append((section_name, start, self.fileobj.tell(), sectionData))
                #if section_name == b"TXET":
                #    print(sectionData)
            else:
                raise RuntimeError("Unknown section: {0}\nCurrent position offset: {1}"
                                   "".format(section_name, hex(self.fileobj.tell()) ))

            
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
        



if __name__ == "__main__":
    #filename = "frontend_0_Level.res"
    import os
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

        with open(path, "rb") as inputfile:
            rxet = RXET(inputfile)
            misc, data = rxet.parse_rxet()

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
