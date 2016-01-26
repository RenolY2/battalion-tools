import os

from lxml import etree
from bw_read_xml import BattWarsLevel, BattWarsObject



if __name__ == "__main__":
    filedir = "BattalionWars/BW2/Data/CompoundFiles/"

    filename = "unitspritelistBW2.txt"

    with open(filename, "w") as f:
        f.write("")

    with open(filename, "a") as f:
        for filename in os.listdir(filedir):
            if not filename.endswith("Level.xml"):
                continue

            f.write("=\n")
            f.write("=\n")
            f.write("="+filename+"\n")
            f.write("=\n")
            with open(filedir+filename, "r") as f_level:
                bw_level = BattWarsLevel(f_level)

                textures = []
                for obj_id, obj in bw_level.obj_map.items():
                    if obj.type == "cTextureResource" and obj.has_attr("mName"):
                    #if obj.type == "cNodeHierarchyResource" and obj.has_attr("mName"):
                        textures.append(obj.get_attr_value("mName"))

                textures.sort()
                for tex in textures:
                    f.write(filename)
                    f.write("/")
                    f.write(tex)
                    f.write("\n")