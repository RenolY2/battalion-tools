import struct

from bw_archive.bw_archive import BWArchive

if __name__ == "__main__":
    import os

    dir = "BattalionWars/BW1/Data/CompoundFiles"
    files = os.listdir(dir)

    out = "test.res"

    sub_sections = [b"RXET", b"PRCS"]

    for filename in files:
        if not filename.endswith(".res"):
            continue

        path = os.path.join(dir, filename)

        with open(path, "rb") as f:
            arc = BWArchive(f)

        with open(out, "wb") as f:
            arc.write(f)

        with open(path, "rb") as f:
            test1 = f.read()

        with open(out, "rb") as f:
            test2 = f.read()

        print(path, out)
        print(test1 == test2)
        print(len(test1), len(test2))
        #assert test1 == test2

        for i, values in enumerate(zip(test1, test2)):
            c1, c2 = values
            if c1 != c2:
                raise RuntimeError("Difference at {0}".format(hex(i)))

        """
        for i, entry in enumerate(arc.entries):
            if entry.name in (b"LDOM", b"MINA", b"FEQT", b"PRCS"):
                with open("res_dump/{0}-{1}.bin".format(entry.name, i), "wb") as f:
                    name, size, data = entry.pack()
                    f.write(data)

        print([x.name for x in arc.entries])
        """
        break