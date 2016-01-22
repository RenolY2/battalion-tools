

if __name__ == "__main__":
    import os
    from rxet_parser import RXET
    import json

    dir = "BattalionWars/BW1/Data/CompoundFiles"
    files = os.listdir(dir)

    outdir = "pim_raw/"

    txet_data = {}
    #print(files)

    for filename in ["frontend_0_Level.res"]:#"C1_OnPatrol_Level.res"]:
        if not filename.endswith(".res"):
            continue

        txet_data[filename] = []
        entities = []
        path = os.path.join(dir, filename)

        print(filename)

        with open(path, "rb") as inputfile:
            rxet = RXET(inputfile)
            misc, data = rxet.parse_rxet(strict=False)



        base_name = filename

        for entry in data:
            section_name, start, end, section_data = entry

            file_name = "{base}_{offset}_.{type}".format(base=base_name,
                                                         offset=start,
                                                         type=section_name.decode("ascii").strip())
            if section_name in (b" PIM"):
                print(file_name)
                out_path = os.path.join(outdir, file_name)
                with open(out_path, "wb") as f:
                    f.write(section_data["data"])


