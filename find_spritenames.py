import os

from lxml import etree
from bw_read_xml import BattWarsLevel, BattWarsObject



if __name__ == "__main__":
    filedir = "BattalionWars/BW1/Data/CompoundFiles/"
    with open("unitspritelist.txt", "w") as f:
        f.write("")

    with open("unitspritelist.txt", "a") as f:
        for filename in os.listdir(filedir):
            if not filename.endswith("Level.xml"):
                continue

            f.write("=\n")
            f.write("=\n")
            f.write(filename+"\n")

            with open(filedir+filename, "r") as f_level:
                bw_level = BattWarsLevel(f_level)

                textures = []
                for obj_id, obj in bw_level.obj_map.items():
                    if obj.type == "cTextureResource" and obj.has_attr("mName"):
                        textures.append(obj.get_attr_value("mName"))

                textures.sort()
                for tex in textures:
                    f.write(tex)
                    f.write("\n")