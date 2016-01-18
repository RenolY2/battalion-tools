from lxml import etree
from bw_read_xml import BattWarsLevel, BattWarsObject



if __name__ == "__main__":
    filename = "C1_Tanktics_Level.xml"
    with open("bw1_sandbox/"+filename, "r") as f:
        bw_level = BattWarsLevel(f)

    wf = []
    tt = []

    for obj_id, obj in bw_level.obj_map.items():
        #if "AirVehicle" in obj.type:
        """airvehiclepointers = ("2138048578", "2138048569", "550008123")
        if "cAirVehicle" == obj.type:
            pointer = obj.get_attr_value("mBase")
            if pointer in airvehiclepointers:
                print(obj.name, pointer)
                attr = obj.get_attr("mUnitInstanceFlags")"""
        """if obj.type == "cGroundVehicleBase" and obj.get_attr_value("mArmy") == "eWesternFrontier":
            print(obj.name)
            obj.set_attr_value("mYOffset", "10")
        """
        if obj.type == "cAirVehicle":
            obj.set_attr_value("mUnitInstanceFlags", "0")


        if obj.type == "sAirVehicleBase":
            print(obj.name)
            obj.set_attr_value("mArmy", "eWesternFrontier")
            obj.set_attr_value("mUnitFlags", "147465")
            obj.set_attr_value("mNoMap", "eFalse")
            obj.set_attr_value("mNoRadar", "eFalse")
            obj.set_attr_value("mMaxHealth", "10000")

            obj.get_attr("mDamageFactor")[0].text = "0.0"
            obj.set_attr_value("mRammingResistance", "1000.0")
            #node = obj.attributes["mArmy"]
            #if node[0].text == "eTundranTerritories" and obj.has_attr("mUnitInstanceFlags"):
            #if node[0].text == "eTundranTerritories": #obj.has_attr("mUnitInstanceFlags"):
                #print(obj.name)
                #print(obj.get_attr_value("mUnitInstanceFlags"))
                #node[0].text = "eWesternFrontier"

        """     if obj.has_attr("mArmy"):
            if obj.get_attr_value("mArmy") == "eWesternFrontier":
                wf.append(obj_id)
            else:
                tt.append(obj_id)

    for obj_id in wf:
        obj = bw_level.obj_map[obj_id]

        obj.set_attr_value("mArmy", "eTundranTerritories")

    for obj_id in tt:
        obj = bw_level.obj_map[obj_id]

        obj.set_attr_value("mArmy", "eWesternFrontier")

    for obj_id, obj in bw_level.obj_map.items():
        if obj.type == "cCamera" and obj.get_attr_value("mCamType") == "eCAMTYPE_CHASETARGET":
            target = obj.get_attr_value("mTarget")
            if target == "0": continue

            for obj_id2 in tt:
                if bw_level.obj_map[obj_id2].type == "sTroopBase":
                    bw_level.obj_map[target].set_attr_value("mBase", obj_id2)
                    print("replaced target base with", obj_id2)
                    break"""


    with open(filename, "wb") as f:
        bw_level._tree.write(f)