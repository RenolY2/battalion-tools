__author__ = 'User'
import struct
from struct import unpack


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


def decode_palette_format(pix, pic_data, palette_data, mode):
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
                except IndexError as e:
                    """print(x, y, xsize, ysize)
                    print(ix, iy)
                    raise"""
                    pass
                #except struct.error:
                #    print(len(pixels))

        x += 8
        if x >= xsize:
            x = 0
            y += 4


# For decoding palette colors
def palette_color_decode(pointer, color_palette, mode):
    color = color_palette[pointer*2:(pointer+1)*2]
    #if len(color) < 2:
    #    return pointer, pointer, pointer, 255#
    color = color.ljust(2, b"\xFF")
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


    from rxet_parser import RXET

    MODE_P8 = 0
    MODE_DXT1 = 1

    dir = "BattalionWars/BW2/Data/CompoundFiles"
    #files = ["C1_OnPatrol_Level.res"] #["frontend_0_Level.res", "frontend_1_Level.res", ] #os.listdir(dir)
    files = os.listdir(dir)
    #files = ["MP10_Level.res"]
    outdir = "out/pics_dump"

    txet_data = {}

    xsize, ysize = None, None


    for filename in files:
        if not filename.endswith(".res"):
            continue

        pics_dir_path = os.path.join("pics_dump", "bw2", filename+"_dir")

        try:
            os.mkdir(pics_dir_path)
        except Exception as e:
            pass

        path = os.path.join(dir, filename)

        with open(path, "rb") as f:
            rxet_archive = RXET(f, "BW2")
            misc, entries = rxet_archive.parse_rxet(strict=False)

        found_txet = False
        txet_entry = None
        mode = None
        pix = None

        for i, entry in enumerate(entries):
            section_name, start, end, section_data = entry

            if section_name == b"DXTG":
                xsize = section_data.size_x
                ysize = section_data.size_y

                if xsize <= 512 and ysize <= 512:
                    pass
                else:
                    continue

                if b"TXD" in section_data.image_type:
                    mode = MODE_DXT1
                elif b"P8" in section_data.image_type:
                    mode = MODE_P8
                else:
                    mode = None

                if mode in (MODE_P8, MODE_DXT1):
                    print(section_data.name, xsize, ysize)
                    pic = Image.new("RGBA", (xsize, ysize))
                    pix = pic.load()

                    out_name = "{name}_{base}_{offset}_{txetoffset}_.{type}.png".format(
                        base=filename,
                        name=section_data.name.decode("ascii"),
                        offset=hex(start),
                        txetoffset=start,
                        type=section_name.decode("ascii"))

                    if mode == MODE_P8:
                        lap = entries[i+1]
                        palette_data = lap[3].data

                        pim = entries[i+2]
                        pic_data = pim[3].data
                        #print(xsize*ysize, len(pic_data))
                        palette_mode = 8#section_data["unknown_int07"]

                        decode_palette_format(pix, pic_data, palette_data, palette_mode)

                    elif mode == MODE_DXT1:
                        pim = entries[i+1]
                        pic_data = pim[3].data

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
                                    #try:
                                    if x+ix+iix < xsize and y+iy+iiy < ysize:
                                        pix[x+ix+iix,y+iy+iiy] = r, g, b, a
                                    else:
                                        print("tried to write outside of bounds:", xsize, ysize, x+ix+iix, y+iy+iiy)

                            x += 8
                            if x >= xsize:
                                x = 0
                                y += 8


                    out_path = os.path.join(pics_dir_path, out_name)
                    pic.save(out_path, "PNG")
                    print(out_path, "saved")

