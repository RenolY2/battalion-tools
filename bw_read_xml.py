from lxml import etree
from copy import copy


class BattWarsObject(object):
    def __init__(self, obj):
        self._attributes = {}

        self.type = obj.get("type")
        self.id = obj.get("id")
        self._xml_node = obj

        # We will create a name for this object by putting the type and ID together.
        self.name = "{0}[{1}]".format(self.type, self.id)

        for attr in obj:
            assert attr not in self._attributes
            self._attributes[attr.get("name")] = attr

    @property
    def attributes(self):
        return self._attributes

    def has_attr(self, name):
        return name in self._attributes

    def get_attr(self, name):
        return self._attributes[name]

    def get_attr_type(self, name):
        return self._attributes[name].get("type")

    def get_attr_elements(self, name):
        return [elem.text for elem in self._attributes[name]]

    # Use this for attributes that have only 1 element
    def get_attr_value(self, name):
        return self._attributes[name][0].text

    def set_attr_value(self, name, val):
        self._attributes[name][0].text = val


class BattWarsLevel(object):
    def __init__(self, fileobj):
        self._tree = etree.parse(fileobj)
        self._root = self._tree.getroot()

        self.obj_map = {}
        for obj in self._root:
            bw_object = BattWarsObject(obj)
            self.obj_map[bw_object.id] = bw_object


    # The root of a BW level xml file contains the objects
    # used by that level.
    @property
    def objects(self):
        return self._root

    def get_attributes(self, obj):
        return []


def create_object_hierarchy(id_map):
    hierarchy = {}
    never_referenced = {obj_id: True for obj_id in id_map.keys()}

    for obj_id, obj in id_map.items():
        if obj.has_attr("mBase"):
            # In the xml file mBase has the type pointer, but it's actually
            # the ID of a different object in the file.
            pointer = obj.get_attr_value("mBase")
            assert pointer in id_map

            if obj.id not in hierarchy:
                del never_referenced[obj_id]
                hierarchy[obj.id] = pointer
            else:
                raise RuntimeError("one object shouldn't have more than 1 reference")

    return hierarchy, never_referenced

def create_ref(ref, hierarchy, id_map):
    if ref.id not in hierarchy:
        return ref.name
    else:
        return ref.name + " => " + create_ref(id_map[hierarchy[ref.id]], hierarchy, id_map)

if __name__ == "__main__":
    with open("bw1_sandbox/C1_Gauntlet_Level.xml", "r") as f:
        bw_level = BattWarsLevel(f)

    types = {}
    id_map = {}

    for obj in bw_level.objects:
        bw_object = BattWarsObject(obj)
        if bw_object.type not in types:
            types[bw_object.type] = 1
        else:
            types[bw_object.type] += 1

        assert bw_object.id not in id_map
        id_map[bw_object.id] = bw_object

    # Never referenced actually doesn't mean that it isn't referenced at all,
    # but that it isn't referenced in a mBase attribute
    hierarchy, never_referenced = create_object_hierarchy(id_map)
    print(never_referenced)
    with open("hierarchy.txt", "w") as f:
        f.write("")

    with open("hierarchy.txt", "a") as f:
        for obj_id in sorted(id_map.keys()):
            obj = id_map[obj_id]
            if obj_id in hierarchy:
                f.write(create_ref(obj, hierarchy, id_map)+"\n")

    print("done")









