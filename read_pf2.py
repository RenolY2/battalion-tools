import os
from struct import unpack
from PIL import Image

def decode_rgb565(color_val):
    b = (color_val & 0b11111) * (256//32)
    g = ((color_val >> 5) & 0b111111) * (256//64)
    r = ((color_val >> 11) & 0b11111) * (256//32)
    return r, g, b, 255


if __name__ == "__main__":
    #input_filepath = os.path.join("bw2_sandbox", "SP_1.1.pf2")
    in_dir = "BattalionWars/BW2/Data/CompoundFiles"
    files = os.listdir(in_dir)

    common_values = {}

    for filename in files:
        if not filename.endswith(".pf2"):
            continue

        in_path = os.path.join(in_dir, filename)
        with open(in_path, "rb") as f:
            data = f.read(0x180000)

        pic = Image.new("RGBA", (512, 512))
        pix = pic.load()

        pic2 = Image.new("RGBA", (512, 512))
        pix2 = pic2.load()

        #pic3 = Image.new("RGBA", (512, 512))
        #pix3 = pic3.load()

        #for x in range(128):
        #    for y in range(128):
        print(filename)
        for i in range(0, len(data)//6):
                x = (i) % 512
                y = (i) // 512
                if x < 256:
                    x *= 2
                else:
                    x = x - 256
                    x *= 2
                    x += 1
                #index = y*128 + x
                #print(i)
                entry = data[i*6: (i+1)*6]
                col = unpack("BBBBBB", entry)

                color1 = col[3:]
                color2 = col[0:3]

                if entry not in common_values:
                    common_values[entry] = True

                i = 0

                for pix_, color in ((pix, color1), (pix2, color2)):#(pix, col1), (pix2, col2), (pix3, col3)):

                    #r, g, b, a = decode_rgb565(color)
                    #g = color & 0xFF
                    #b = color >> 2
                    #r = 0

                    r, g, b = color


                    #print("woohoo", r, g, b)
                    #if col1 == 0xFF0F and i == 0:
                    #    pix_[x,511-y] = r, g, b, 0
                    #else:
                    pix_[x,511-y] = r, g, b, 255

                    i+=1

        out = os.path.join("out", filename+".png")
        out2 = os.path.join("out", filename+"2.png")
        #out3 = os.path.join("out", filename+"3.png")

        pic.save(out, "PNG")
        pic2.save(out2, "PNG")
        #pic3.save(out3, "PNG")



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

            f.write("\n")

