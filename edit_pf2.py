from struct import unpack, pack


def make_entire_map_accessible(infile, outfile):
    data = infile.read(0x180000)
    rest = infile.read()
    outfile.seek(0)

    print(len(data), len(rest))
    for i in range(0, len(data)//6):
        entry = data[i*6:(i+1)*6]

        val1, val2, terraindata = unpack("HHH", entry)
        val2 |= 0x00F0

        modified = pack("HHH", val1, val2, terraindata)
        outfile.seek(i*6)
        outfile.write(modified)

    outfile.seek(0x180000)
    outfile.write(rest)

if __name__ == "__main__":
    import os

    in_dir = "BattalionWars/BW2/Data/CompoundFiles"
    files = os.listdir(in_dir)

    for filename in files:
        if filename.endswith(".pf2"):

            path = os.path.join(in_dir, filename)

            with open(path, "rb") as f:
                with open(os.path.join("out", "modified"+filename), "wb") as out_f:
                    make_entire_map_accessible(f, out_f)