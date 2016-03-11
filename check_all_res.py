if __name__ == "__main__":
    import os

    from bw_archive.bw_archive import BWArchive
    from bw_read_xml import BattWarsLevel

    in_dir = os.path.join("BattalionWars", "BW1", "Data", "CompoundFiles")

    res_files = filter(lambda x: x.endswith(".res"), os.listdir(in_dir))
    types = {}

    for filename in res_files:
        path = os.path.join(in_dir, filename)
        xmlpath = path[:-4]+".xml"
        print("---", filename, "---")
        with open(path, "rb") as f:
            bw_arc = BWArchive(f)

        with open(xmlpath, "r") as f:
            bw_xml = BattWarsLevel(f)
        #print("--------------------------\n")
        #print(filename)
        #print([ (entry.name, bytes(entry.res_name)) for entry in filter(lambda x:x.name == b"PRCS", bw_arc.entries)])

        for obj_id, obj in bw_xml.obj_map.items():
            for attr in obj.attributes:
                if obj.has_attr("mName"):
                    assert obj.get_attr_type("mName") == "cFxString8"
                    if obj.type == "cTroop" and obj.get_attr_value("mName") is not None:
                        print(obj.get_attr_value("mName"))
                    types[obj.type] = True

        # Check if the sounds, effects, models and textures referenced in the XML file do exist in the RES file
        for res_type in ["sSampleResource", "cTequilaEffectResource", "cNodeHierarchyResource", "cTextureResource"]:
            if res_type not in bw_xml.resources:
                continue

            for obj in bw_xml.resources[res_type]:
                name = obj.get_attr_value("mName")
                res = bw_arc.get_resource(res_type, bytes(name, encoding="utf-8"))
                #print(name, res)
                #assert res is not None

                # if res is None, then the resource couldn't be found and we print it
                if res is None:
                    print(name)

        # Now we check if the models and textures from the RES file exist in the 
        for res in bw_arc.models:
            name = str(bytes(res.res_name).strip(b"\x00"), encoding="ascii")
            xml_res = bw_xml.get_resource("cNodeHierarchyResource", name)
            assert xml_res.get_attr_value("mName") == name

        for res in bw_arc.textures:
            name = str(bytes(res.res_name).strip(b"\x00"), encoding="ascii")
            xml_res = bw_xml.get_resource("cTextureResource", name)
            assert xml_res.get_attr_value("mName").upper() == name.upper()

        """print("--", filename)
        print("models:", len(bw_arc.models), "anims:", len(bw_arc.animations), "sounds:", len(bw_arc.sounds), "effects:", len(bw_arc.effects))
        for obj_id, obj in bw_xml.obj_map.items():
            if obj.type == "cWorldFreeListSizeLoader":
                freelist = obj

        print(", ".join("{0}: {1}".format(x, freelist.get_attr_value(x)) for x in freelist.attributes))
        """

    for x in sorted(types.keys()):
        print(x)