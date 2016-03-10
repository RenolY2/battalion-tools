import os

from PIL import Image, ImageDraw
from bw_read_xml import BattWarsLevel

def draw_box(draw, startx, starty, xsize, ysize, angle, color):
    """for ix in range(xsize):
        for iy in range(ysize):
            try:
                pix[startx+ix, starty+iy] = color
            except:
                print(startx+ix, starty+iy)
    """

    draw.polygon(xy=((startx, starty), (startx+xsize, starty),
                     (startx+xsize, starty+ysize), (startx, starty+ysize)),
                 outline=color)


if __name__ == "__main__":
    dir_path = os.path.join("BattalionWars", "BW1", "Data", "CompoundFiles")

    max_size = 0
    max_x = 0
    max_y = 0
    min_x = 0
    min_y = 0

    for filename in filter(lambda x: x.endswith("_Level.xml"), os.listdir(dir_path)):
        with open(os.path.join(dir_path, filename)) as f:
            in_xml = BattWarsLevel(f)

        pic = Image.new("RGBA", (256, 256))
        pix = pic.load()
        draw = ImageDraw.Draw(pic)

        for obj_id, obj in in_xml.obj_map.items():

            if obj.type == "cMapZone":
                matrname = "mMatrix"
            elif obj.has_attr("Mat"):
                matrname = "Mat"
            else:
                matrname = None

            if matrname is not None:
                matr = [x for x in map(lambda x: float(x), obj.get_attr_value(matrname).split(","))]

                x = matr[12]//16 + 128
                y = matr[14]//16 + 128

                if obj.type == "cMapZone":
                    dim = [x for x in map(lambda x: int(float(x)), obj.get_attr_value("mSize").split(","))]
                    width, height = dim[0]//16, dim[2]//16
                    zonetype = obj.get_attr_value("mZoneType")

                    x -= width//2
                    y -= height//2

                    if zonetype == "ZONETYPE_NOGOAREA":
                        #c = (255, 0, 0, 255)
                        draw_box(draw, x, y, width, height, 1, (255, 0, 0, 255))
                    elif zonetype == "ZONETYPE_DEFAULT":
                        c = (127, 127, 127, 255)
                        draw_box(draw, x, y, width, height, 1, c)
                    elif zonetype == "ZONETYPE_MISSIONBOUNDARY":
                        c = (255, 255, 0, 255)
                        draw_box(draw, x, y, width, height, 1, c)
                    else:
                        print(zonetype)
                        c = (255, 255, 255, 255)
                    x += width//2
                    y += height//2
                else:
                    c = (0,0 , 255)
                    if obj.id == "450001876":
                        for ix in range(-3, 3):
                            for iy in range(-3, 3):
                                pix[x+ix, y+iy] = (255, 0, 255)
                pix[x,y] = c

        pic.save(os.path.join("bw_boundaries", filename+".png"), "PNG")
    print(max_x, max_y, min_x, min_y)