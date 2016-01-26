

def decode_rgb565(color_val):
    b = (color_val & 0b11111) * (256//32)
    g = ((color_val >> 5) & 0b111111) * (256//64)
    r = ((color_val >> 11) & 0b11111) * (256//32)
    return r, g, b, 255


def addrgba(col1, col2):
    return col1[0]+col2[0], col1[1]+col2[1], col1[2]+col2[2], col1[3]+col2[3]


def multrgba(col, c):
    return col[0] * c, col[1] * c, col[2] * c, col[3] * c


def divrgba(col, c):
    return col[0] // c, col[1] // c, col[2] // c, col[3] // c


def decode_palette_format(pix, pic_data, palette_data):
    x, y = 0, 0

    for i in range(0, len(pic_data)//32):
        pixels = pic_data[i*32:(i+1)*32]

        # For images that use the palette, the pixels are arranged
        # in 8 by 4 pixel blocks
        for ix in range(8):
            for iy in range(4):
                try:
                    pointer = pixels[iy*8+ix]

                    r, g, b, a = palette_color_decode(pointer, palette_data, mode)
                    pix[x+ix, y+iy] = r, g, b, a
                except Exception as e:
                    print(x, y, xsize, ysize)
                    raise

        x += 8
        if x >= xsize:
            x = 0
            y += 4


# For decoding palette colors
def palette_color_decode(pointer, color_palette, mode):
    color = color_palette[pointer*2:(pointer+1)*2]
    color_val = unpack(">H", color)[0]

    if mode == 8:
        # If most significant bit is set, we parse the int
        # as RGB555. Otherwise we parse it as RGBA4443
        if color_val >> 15:
            a = 255
            b = (color_val & 0b11111) * (256//32)
            g = ((color_val >> 5) & 0b11111) * (256//32)
            r = ((color_val >> 10) & 0b11111) * (256//32)
        else:
            b = ((color_val >> 0) & 0b1111) * (256//16)
            g = ((color_val >> 4) & 0b1111) * (256//16)
            r = ((color_val >> 8) & 0b1111) * (256//16)
            a = ((color_val >> 12) & 0b111) * (256//8)
    elif mode == 2:
        # Mode=2 is probably grayscale
        r, g, b, a = pointer, pointer, pointer, 255
    #elif mode == 5:
    #    a = 255
    #    b = (color_val & 0b11111) * (256//32)
    #    g = ((color_val >> 5) & 0b111111) * (256//64)
    #    r = ((color_val >> 11) & 0b11111) * (256//32)
    #    #r, g, b, a = pointer, pointer, pointer, 255"""
    else:
        r, g, b, a = pointer, pointer, pointer, 255

    return r, g, b, a

if __name__ == "__main__":
    import os
    from math import sqrt
    from PIL import Image
    from struct import unpack

    from rxet_parser import RXET

    MODE_P8 = 0
    MODE_DXT1 = 1

    dir = "BattalionWars/BW1/Data/CompoundFiles"
    #files = ["C1_OnPatrol_Level.res"] #["frontend_0_Level.res", "frontend_1_Level.res", ] #os.listdir(dir)
    files = os.listdir(dir)
    outdir = "out/"

    txet_data = {}

    xsize, ysize = None, None


    for filename in files:
        if not filename.endswith(".res"):
            continue

        path = os.path.join(dir, filename)

        with open(path, "rb") as f:
            rxet_archive = RXET(f)
            misc, entries = rxet_archive.parse_rxet(strict=False)

        found_txet = False
        txet_entry = None
        mode = None
        pix = None

        for i, entry in enumerate(entries):
            section_name, start, end, section_data = entry

            if section_name == b"TXET":
                found_txet = True

                if "pim_count" in section_data and section_data["pim_count"] > 1:
                    found_txet = False
                    mode = None
                    continue

                txet_entry = entry
                xsize = section_data["xsize"]
                ysize = section_data["ysize"]

                if "unknown_string" in section_data and section_data["unknown_string"].startswith(b"P8"):
                    mode = MODE_P8
                elif entries[i+1][0] == b"DXT1":
                    mode = MODE_DXT1
                else:
                    mode = None

                if mode in (MODE_P8, MODE_DXT1):
                    pic = Image.new("RGBA", (xsize, ysize))
                    pix = pic.load()

                    out_name = "{name}_{base}_{offset}_{txetoffset}_.{type}.png".format(
                        base=filename,
                        name=txet_entry[3]["name_string"].decode("ascii").strip("\x00"),
                        offset=hex(start),
                        txetoffset=txet_entry[1],
                        type=section_name.decode("ascii").strip())

                    if mode == MODE_P8:
                        lap = entries[i+1]
                        palette_data = lap[3]["data"]

                        pim = entries[i+2]
                        pic_data = pim[3]["data"]
                        print(xsize*ysize, len(pic_data))
                        palette_mode = section_data["unknown_int07"]

                        decode_palette_format(pix, pic_data, palette_data)

                    elif mode == MODE_DXT1:
                        dxt_info = entries[i+1]
                        assert dxt_info[0] == b"DXT1"

                        pim = entries[i+2]
                        pic_data = pim[3]["data"]

                        x, y = 0, 0

                        for ii in range(0, len(pic_data)//8, 4):
                            for ii2 in range(0, 4):
                                block = pic_data[(ii+ii2)*8:(ii+ii2+1)*8]

                                #col0, col1, pixmask = unpack(">HHI", block)
                                col0, col1 = unpack(">HH", block[:4])
                                pixmask = unpack(">I", block[4:])[0]
                                color0 = decode_rgb565(col0)
                                color1 = decode_rgb565(col1)
                                iix = (ii2 % 2)*4
                                iiy = (ii2 // 2)*4


                                if col0 > col1:
                                    #col2 = (2*col0 + col1) // 3
                                    #col3 = (2*col1 + col0) // 3


                                    color2 = divrgba(addrgba(multrgba(color0, 2), color1), 3)
                                    color3 = divrgba(addrgba(multrgba(color1, 2), color0), 3)

                                    #colortable = (decode_rgb565(col0), decode_rgb565(col1),
                                    #              decode_rgb565(col2), decode_rgb565(col3))

                                else:
                                    #col2 = (col0 + col1) // 2
                                    #col3 = 0

                                    color2 = divrgba(addrgba(color0, color1), 2)
                                    color3 = (0, 0, 0, 0)

                                    #colortable = (decode_rgb565(col0), decode_rgb565(col1),
                                    #              decode_rgb565(col2), (0, 0, 0, 0))


                                colortable = (color0, color1, color2, color3)
                                #colortable = (color0, color0, color1, color1)
                                #for ix in range(4):
                                #    for iy in range(4):
                                for iii in range(16):
                                    iy = iii // 4
                                    ix = iii % 4
                                    index = (pixmask >> ((15-iii)*2)) & 0b11
                                    #col = index * (256//4)
                                    #a = 255
                                    #r, g, b, a = color0

                                    r, g, b, a = colortable[index]
                                    pix[x+ix+iix,y+iy+iiy] = r, g, b, a

                            x += 8
                            if x >= xsize:
                                x = 0
                                y += 8



                    out_path = os.path.join("pics_dump", out_name)
                    pic.save(out_path, "PNG")
                    print(out_path, "saved")

