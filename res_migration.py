import networkx as nx


def get_dependencies(bw_dependency_graph, obj_id):
    return [node for node in nx.bfs_tree(bw_dependency_graph, obj_id)]

def get_postorder_dep(bw_dependency_graph, obj_id):
    return [node for node in nx.dfs_postorder_nodes(bw_dependency_graph, obj_id)]



def calc_dependency_graph(bw_level):
    obj_graph = nx.DiGraph()

    for obj_id, obj in bw_level.obj_map.items():
        obj_graph.add_node(obj.id)

        for attr in obj.attributes:
            #if obj.get_attr_type(attr)[0] in ("s", "c"):

            if obj.get_attr_tag(attr) in ("Resource", "Pointer"):
                attr_type = obj.get_attr_type(attr)

                #value = obj.get_attr_value(attr)
                for value in obj.get_attr_elements(attr):
                    if value in bw_level.obj_map:
                        #print(attr, obj.get_attr_type(attr))
                        obj_graph.add_edge(obj.id, bw_level.obj_map[value].id)

    return obj_graph

def get_resource(bwlevel, restype, name):
    if restype == "sSampleResource":
        reslist = bwlevel.sounds

        for res, res_data in reslist:
            if bytes(res.res_name).strip(b"\x00") == name:
                return res, res_data
        return None

    elif restype == "cTequilaEffectResource": reslist = bwlevel.effects
    elif restype == "cNodeHierarchyResource": reslist = bwlevel.models
    elif restype == "cTextureResource": reslist = bwlevel.textures
    else: raise RuntimeError("What: {0}".format(restype))

    for res in reslist:
        if bytes(res.res_name).strip(b"\x00") == name:
            return res

    return None



if __name__ == "__main__":
    import os
    from bw_archive.bw_archive import BWArchive
    from bw_read_xml import BattWarsLevel

    in_dir = os.path.join("BattalionWars", "BW1", "Data", "CompoundFiles")


    in_level = "C3_PassThePort"
    out_level = "C2_Exodus"

    in_res_filename = in_level+"_Level.res"
    in_xml_filename = in_level+"_Level.xml"

    out_res_filename = out_level+"_Level.res"
    out_xml_filename = out_level+"_Level.xml"

    out_res_modded = out_res_filename+""
    out_xml_modded = out_xml_filename+""

    # Read the xml files for the two levels
    with open(os.path.join(in_dir, in_xml_filename), "r") as f:
        in_xml = BattWarsLevel(f)

    with open(os.path.join(in_dir, out_xml_filename), "r") as f:
        out_xml = BattWarsLevel(f)

    # Read the res files for the two levels
    with open(os.path.join(in_dir, in_res_filename), "rb") as f:
        in_res = BWArchive(f)

    with open(os.path.join(in_dir, out_res_filename), "rb") as f:
        out_res = BWArchive(f)

    graph = calc_dependency_graph(in_xml)

    battlestation = "2138048269"
    bsta_dependencies = get_dependencies(graph, battlestation)

    additional = ["2138046784", "2138046782", "2138046783", "250000932"]
    #bsta_dependencies.append("2138046784")
    assert all(x not in bsta_dependencies for x in additional)
    bsta_dependencies.extend(additional)
    needed_dependencies = [dep for dep in filter(lambda x: x not in out_xml.obj_map, bsta_dependencies)]
    #print([x for x in needed_dependencies])
    hierarchy = ["sSampleResource", "cTequilaEffectResource", "cTextureResource", "cNodeHierarchyResource"]#,
                 #"cSimpleTequilaTaggedEffectBase"]

    for obj_id in needed_dependencies:
        obj = in_xml.obj_map[obj_id]
        #if obj.type not in hierarchy:
        #    print(obj.name)

        strcount = 0
        for attr in obj.attributes:
            if obj.get_attr_type(attr) == "cFxString8":
                #strcount += 1
                strname = obj.get_attr_value(attr)
                print(obj.name, strname)

                res = get_resource(in_res, obj.type, bytes(strname, encoding="utf-8"))
                assert res is not None

                if obj.type == "cTextureResource":
                    print("texname:",bytes(res.res_name))
                    out_res.ftb.entries.insert(0, res)
                elif obj.type == "sSampleResource":
                    res_name, res_data = res
                    #out_res.dnos.entries.append(res_name)
                    #out_res.dnos.entries.append(res_data)
                elif obj.type == "cTequilaEffectResource":
                    #out_res.entries.append(res)
                    pass
                elif obj.type == "cNodeHierarchyResource":
                    print("modelname:", bytes(res.res_name))
                    #out_res.entries.append(res)
                    #out_res.add_model(res)
                    #if res.res_name == b"VWFBSTAH_TRAC_R":
                    if res.res_name == b"VWFBSTAH":
                        replace_res = get_resource(out_res, obj.type, b"VWFHTNKH")
                        assert len(res.entries) == 1
                        assert len(replace_res.entries) == 1
                        replace_res.entries[0] = res.entries[0]
                else:
                    raise RuntimeError("unknown: "+obj.type)

    print(len(in_xml.obj_map), len(out_xml.obj_map))
    for i, needed in enumerate(hierarchy):
    #if True:
        for obj_id in needed_dependencies:
            obj = in_xml.obj_map[obj_id]
            assert obj.id not in out_xml.obj_map
            if obj.type != needed:
                continue

            print("added object:", obj.name, obj.type)

            out_xml._root.append(obj._xml_node)




    #for obj in needed_dependencies:

    with open(out_res_modded, "wb") as f:
        out_res.write(f)

    with open(out_xml_modded, "wb") as f:
        out_xml._tree.write(f)





