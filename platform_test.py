import unittest

from PyNite import FEModel3D

from utils.parser import read_json


class SteelMaterial:
    """Material used for Finite Element Analysis"""

    name = "Steel"
    e = 199.95  # (GPa) Modulus of elasticity
    g = 78.60  # GPa Shear modulus
    nu = 0.30  # Poisson's ratio
    rho = 7833.41  # kg per cubic metre Density


class SteelSectionProperties:
    """Section Properties used for Finite Element Analysis"""

    iy = 0.0000072  # (m**4) Weak axis moment of inertia
    iz = 0.000085  # (m**4) Strong axis moment of inertia
    j = 1.249e-7  # (m**4) Torsional constant
    a = 0.0049  # (m**2) Cross-sectional area


class UnitMaterial:
    """Material used for Finite Element Analysis"""

    name = "Custom"
    e = 1  # (ksi) Modulus of elasticity
    g = 1  # (ksi) Shear modulus
    nu = 1  # Poisson's ratio
    rho = 1  # (kci) Density


class UnitSectionProperties:
    """Section Properties used for Finite Element Analysis"""

    iy = 1  # (in**4) Weak axis moment of inertia
    iz = 1  # (in**4) Strong axis moment of inertia
    j = 1  # (in**4) Torsional constant
    a = 1  # (in**2) Cross-sectional area


def get_forces(
    material: type[SteelMaterial | UnitMaterial],
    section_properties: type[SteelSectionProperties | UnitSectionProperties],
) -> dict:
    nodes, edges = read_json("output/dino.json")
    truss = FEModel3D()
    truss.add_material(material.name, material.e, material.g, material.nu, material.rho)

    for node in nodes:
        truss.add_node(node.id, node.vec.x, node.vec.y, node.vec.z)
        if node.r_support and node.t_support:
            truss.def_support(
                node.id,
                node.t_support.x,
                node.t_support.y,
                node.t_support.z,
                node.r_support.x,
                node.r_support.y,
                node.r_support.z,
            )
        if node.load:
            if node.load.x != 0:
                truss.add_node_load(node.id, "FX", node.load.x)
            if node.load.y != 0:
                truss.add_node_load(node.id, "FY", node.load.y)
            if node.load.z != 0:
                truss.add_node_load(node.id, "FZ", node.load.z)

    for edge in edges:
        truss.add_member(
            edge.id,
            edge.u.id,
            edge.v.id,
            material.name,
            section_properties.iy,
            section_properties.iz,
            section_properties.j,
            section_properties.a,
        )
        truss.def_releases(
            edge.id,
            False,
            False,
            False,
            False,
            True,
            True,
            False,
            False,
            False,
            False,
            True,
            True,
        )

    if material == UnitMaterial and section_properties == UnitSectionProperties:
        for member in truss.Members.values():
            # 110g per m for d=0,2m beam = 1.08N
            # 275g per m for d=0,5m beam = 2.7N
            self_weight = 1.08
            truss.add_member_dist_load(member.name, "FY", self_weight, self_weight)

    truss.analyze(check_statics=True)
    max_forces = {member.name: member.max_axial() for member in truss.Members.values()}
    return max_forces


result = {
    "steel": {
        "e435af60-22aa-4fa3-a8cc-e879dbf49dbf": -73.3785448747035,
        "9b094159-9b53-4b7a-b3a8-30146783948f": 9.647870195248288,
        "a376e469-f923-4c1e-999b-ceb5ad2cbc77": -8.788644350749848,
        "693ab2bd-d80c-460a-b7a5-aef24f545903": 9.094947017729282e-13,
        "03e060e1-ab12-42c7-bd6f-bd370f66b296": 7.275957614183426e-12,
        "985914c5-7cc7-4bae-9c30-060ed6d3dbcb": -6.366462912410498e-12,
        "b59b3ad1-5fa0-4bb3-8b15-85f1b775fcd4": 7.275957614183426e-12,
        "207b968c-75b0-402b-b1d7-0ad4c717ce66": -6.366462912410498e-12,
        "7960a176-f617-4183-811b-9f612f676220": 3.637978807091713e-12,
        "e3c9863d-6ae7-4d8d-b6d0-4d5c80baff97": -1.5916157281026244e-12,
        "54bfbac9-1abd-4bc7-8774-3cd7924ba98d": 1.000444171950221e-11,
        "937139e7-313e-4b06-8c57-ad03708a6b99": -6.366462912410498e-12,
        "0261b51b-7041-4caf-b79e-4c8fa7c9d06f": 8.185452315956354e-12,
        "9aa05d9d-4dea-43c4-8b31-33ef04834bb9": 4.547473508864641e-13,
        "0118da7f-6660-4701-93bf-8c1f4ee7d200": 1.057287590811029e-11,
        "19135b15-691f-4213-af83-0b07baa56a07": -276.1123003164935,
        "393f0ecf-2844-4782-875b-d16ae5a461ae": -9.094947017729282e-13,
        "25e8fcfa-ab27-4083-81d5-5f4d7f9d21ba": 3.637978807091713e-12,
        "967ec194-88c3-44f5-b134-0dc3be36e6e7": 4.149569576838985e-12,
        "d395c6cc-3ade-454e-82d0-ba2b620bf7df": -9.094947017729282e-12,
        "badaa4fe-c384-47f0-b4b2-8cbe2ba2f684": 0.0,
        "7bcdea3f-c825-4a41-ace2-2789c65302d4": 3.637978807091713e-12,
        "f5cfc8c5-8c4a-4d2b-8811-2417a84fcc5e": 5.4569682106375694e-12,
        "1e09c89d-451f-4d05-bd00-324c86c2dbaa": 0.0,
        "9b61e11a-185c-4f75-93dd-2cfe6c79c66c": -2.7284841053187847e-12,
        "fa073afe-7035-489e-9f5b-84f4884701d1": -4.547473508864641e-12,
        "be9d13fb-0edc-4db8-884d-e6b48c3dcc49": 0.0,
        "1842ddbf-3427-4dac-ae4e-62666ccdf7d5": 2.000888343900442e-11,
        "4705cd5f-604c-442b-8bd1-3ba686a5b735": -1.4551915228366852e-11,
        "8860a365-7064-4a33-aa35-b5a5c049864b": 2.000888343900442e-11,
        "d935c972-96d2-444f-8eb3-06b851507802": -347.23264041853224,
        "549c0819-ad34-4a2b-9a73-f20ac3b4633d": 0.0,
        "23c3ef17-b67c-4d43-b00d-06b9beb87a71": 1.0913936421275139e-11,
        "b2d264b4-2d58-4851-a55c-b18384a0715a": 1.0231815394945443e-11,
        "481e5dc0-1e9d-4031-a3fd-fba5d4875b90": 9.094947017729282e-13,
        "284dd3ed-51ae-495c-8944-ac8c64b18c5c": -1.8189894035458565e-12,
        "e78feb88-85fe-4996-87ea-e56b58469374": -20.853719459938475,
        "74123fff-52b0-40af-b086-99114521fa0d": 10.953023280811067,
        "f73c39f8-1e16-41e0-b9cf-c49af0de7e9e": -24.76400648606392,
        "6270615a-7635-48eb-89ff-68bf1542c243": -15.688603743679778,
        "ae25b293-1ec2-4ead-a42a-b7c28fb8c614": 21.261651001358587,
        "3410f54f-ee78-47f0-a847-33de66c65491": -7.973682526324126,
        "c48630b6-98a9-493e-bc36-6aa5c4c51090": -4.678396223084405,
        "336c2db5-ee02-46fd-8f3f-b4dfb7839f17": -3.637978807091713e-12,
        "8083b0b6-061b-4bc5-bfd2-c10cede65dbf": -7.275957614183426e-12,
        "fe7b3fab-80c3-4163-aa4e-ad09f327861d": 3.637978807091713e-12,
        "a22e925d-1243-430c-a995-f8bdd703bc49": 1.4551915228366852e-11,
        "cb769ace-b89d-42d7-80a9-d431eec5e93e": 1.4551915228366852e-11,
        "35f254a3-8765-4db0-b400-e25751137a15": 1.8189894035458565e-12,
        "d5bf54d2-8fc5-4687-8258-7253fb830e33": 0.0,
        "30865b43-55bc-4b19-adea-02cb7eccc5f1": 0.0,
        "739fa773-14f5-4dab-a896-a10307ae02cd": -5.048696324202865,
        "4b8b6f15-b35d-4efb-b8ed-737d6e9a5532": -17.734799438411756,
        "5329c64b-0948-4044-ab4a-6ddbaf791aff": 19.236375842439884,
        "d8bbcbb3-1bee-4a21-83b6-136cd45a01ec": 18.358197077703608,
        "eab6f5d1-7656-4335-91b5-c61f8ebf2519": 244.6519073561858,
        "56a98dae-ed25-43c2-9112-6019c8f0d796": 53.32595117962512,
        "d3943757-99e1-436a-aa62-5ee97de8ca52": 49.213506012100424,
        "c3ea1ae7-eb1a-42ae-a6e5-528ea9f3614c": -136.19262351620364,
        "6e565aaa-62ea-49f6-9af5-d98982a49017": 316.30356281205536,
        "6767c869-4c9c-4fd9-941e-21b2a5e91a9a": -74.17999330984912,
        "34ad2ea4-1601-4e0f-b6e5-5c0d960a24b1": 565.1864377941441,
        "e958bbd5-0ccf-4961-aa3d-7ea95b633169": 23.107714265254685,
        "82f4366c-c7ee-46c3-83a0-3d46963847a5": -135.68071825231064,
        "ced8dbac-15a2-4c98-abd7-fb8b0b5596d0": 305.2439667246945,
        "574cb57d-057c-463d-acfc-32d16cfb5728": 492.2271929555509,
        "28f03d5f-94c4-420b-9859-6b0052127f0c": -358.6674832011376,
        "8627dc43-64c1-4374-8b77-8add26043e0c": 51.25734489625302,
        "ad3cc1bb-92c5-4a53-a8d7-02f0db377a7f": -136.91360797062987,
        "88792152-efb0-4d77-91f2-327959d3cc2a": -5.043344240951164,
        "1de035f6-2576-41db-ae64-f6d4a9f6a169": -193.81632515099807,
        "45dcb176-1b6d-4958-8925-9ada4da4bd38": 76.10692011314173,
        "5167031b-cc1d-4249-b144-ab38213b6eff": -83.97504371754032,
        "54776ad4-c2d1-4d59-853e-78af6090be51": 358.64896579905263,
        "1a83c37e-2f60-4d57-b6ce-e1840e9eb07a": -205.77572641671625,
        "a1ee0f54-950b-43df-bc66-83a576b4901d": 241.96351559344387,
        "17e56e25-f272-451f-a705-a112443bb16a": 53.26345896034826,
        "35ded22a-763f-4f91-b68d-bc51c787002f": 373.39632836195915,
        "317acb3b-42a6-481b-82bb-8a77b26ace88": 0.0,
        "0cc1710d-9bf2-4b21-b3c5-85a9517f979e": 0.0,
        "61a04207-60a6-4567-94d7-7f900a99dc6a": 0.0,
        "10db9e88-f1f0-44cc-a063-6f20ba6e34ff": -120.8948566409346,
        "4880e981-e84a-4844-8afa-1f0b564bafd6": 53.435984874790144,
        "250c7958-87bb-4317-a596-c8e8d070f09f": 131.44649133535745,
        "5344d2cc-fd72-43e8-bc23-7af8e8e875d3": 179.1524207457768,
        "901162b3-511a-4e57-bce8-19b1b82ff510": 329.16807708463966,
        "8581a05e-4953-4f0d-a169-8e4a67682d79": -339.85624019228186,
        "bd1f88d0-c0d7-46bc-8127-604e59352c01": 0.0,
        "94256d26-016c-43af-94b5-f1c0fe13e007": 0.0,
        "5fd8459a-cca6-4c29-b46b-615b94b00a0e": 0.0,
        "9130b5e2-572c-4644-9c97-7a197b1f11c3": -38.56339406082783,
        "400133ed-1625-404d-bf8f-ddf30f95e1db": 299.31208349469574,
        "1146e4f5-f13b-4a7a-a700-981032aca2f6": 96.81728710931999,
        "34933e83-8339-4851-9d17-e268d08f78cd": 334.42077101020664,
        "42df2202-337c-4784-a9ac-1a6b3af9acf2": -53.83411414750107,
        "4f457b3e-5f6f-49be-be94-03bab7c8cd19": -52.63215950374576,
        "2f218b34-4f9a-4fc2-ac5c-4cc7954327ba": 7.275957614183426e-12,
        "50c583dd-f830-4ecc-8df7-c966f5f4cc7d": 372.5393103853594,
        "fbba3cb1-80c8-467c-a010-6fa4e1d39901": 475.80051848155915,
        "f06f5c2d-ede1-487f-9552-0304865b1ab2": 140.16771712344575,
        "e9216c06-e4da-474c-aa7f-a2293854e154": -91.12145069899361,
    },
    "unit": {
        "e435af60-22aa-4fa3-a8cc-e879dbf49dbf": -26.673127411772537,
        "9b094159-9b53-4b7a-b3a8-30146783948f": 25.345872730761826,
        "a376e469-f923-4c1e-999b-ceb5ad2cbc77": -12.414126438554865,
        "693ab2bd-d80c-460a-b7a5-aef24f545903": -45.78150682,
        "03e060e1-ab12-42c7-bd6f-bd370f66b296": -1.13026512,
        "985914c5-7cc7-4bae-9c30-060ed6d3dbcb": -48.617228958674495,
        "b59b3ad1-5fa0-4bb3-8b15-85f1b775fcd4": 53.30693071337657,
        "207b968c-75b0-402b-b1d7-0ad4c717ce66": 1.136724840423704,
        "7960a176-f617-4183-811b-9f612f676220": 24.620664869086106,
        "e3c9863d-6ae7-4d8d-b6d0-4d5c80baff97": -7.718550070544283,
        "54bfbac9-1abd-4bc7-8774-3cd7924ba98d": 9.26467996,
        "937139e7-313e-4b06-8c57-ad03708a6b99": 43.94957114,
        "0261b51b-7041-4caf-b79e-4c8fa7c9d06f": 32.58651032861128,
        "9aa05d9d-4dea-43c4-8b31-33ef04834bb9": -63.35147884644966,
        "0118da7f-6660-4701-93bf-8c1f4ee7d200": -37.410566392623075,
        "19135b15-691f-4213-af83-0b07baa56a07": -294.7498398843591,
        "393f0ecf-2844-4782-875b-d16ae5a461ae": 5.812801500000001,
        "25e8fcfa-ab27-4083-81d5-5f4d7f9d21ba": 1.1339199999999996,
        "967ec194-88c3-44f5-b134-0dc3be36e6e7": -8.3789806,
        "d395c6cc-3ade-454e-82d0-ba2b620bf7df": 41.0129006,
        "badaa4fe-c384-47f0-b4b2-8cbe2ba2f684": -25.01521118,
        "7bcdea3f-c825-4a41-ace2-2789c65302d4": -3.0023105799999996,
        "f5cfc8c5-8c4a-4d2b-8811-2417a84fcc5e": 43.23448732,
        "1e09c89d-451f-4d05-bd00-324c86c2dbaa": -5.94427412,
        "9b61e11a-185c-4f75-93dd-2cfe6c79c66c": -5.457174719999999,
        "fa073afe-7035-489e-9f5b-84f4884701d1": 7.93488792,
        "be9d13fb-0edc-4db8-884d-e6b48c3dcc49": -7.998723440000001,
        "1842ddbf-3427-4dac-ae4e-62666ccdf7d5": -75.10904348,
        "4705cd5f-604c-442b-8bd1-3ba686a5b735": -46.95795542,
        "8860a365-7064-4a33-aa35-b5a5c049864b": -53.31638538,
        "d935c972-96d2-444f-8eb3-06b851507802": -325.3956030035118,
        "549c0819-ad34-4a2b-9a73-f20ac3b4633d": 10.48159858,
        "23c3ef17-b67c-4d43-b00d-06b9beb87a71": -57.2383727,
        "b2d264b4-2d58-4851-a55c-b18384a0715a": -25.751273299999998,
        "481e5dc0-1e9d-4031-a3fd-fba5d4875b90": 22.639411916225875,
        "284dd3ed-51ae-495c-8944-ac8c64b18c5c": -5.922396922818855,
        "e78feb88-85fe-4996-87ea-e56b58469374": -31.1923672655567,
        "74123fff-52b0-40af-b086-99114521fa0d": 25.59966088072482,
        "f73c39f8-1e16-41e0-b9cf-c49af0de7e9e": -36.68431712584448,
        "6270615a-7635-48eb-89ff-68bf1542c243": -19.23342420083639,
        "ae25b293-1ec2-4ead-a42a-b7c28fb8c614": 81.78393940619272,
        "3410f54f-ee78-47f0-a847-33de66c65491": -29.28292004588523,
        "c48630b6-98a9-493e-bc36-6aa5c4c51090": -14.772817641674775,
        "336c2db5-ee02-46fd-8f3f-b4dfb7839f17": 12.11870882,
        "8083b0b6-061b-4bc5-bfd2-c10cede65dbf": -7.9576521200000006,
        "fe7b3fab-80c3-4163-aa4e-ad09f327861d": 34.26084106,
        "a22e925d-1243-430c-a995-f8bdd703bc49": 0.057883680000000236,
        "cb769ace-b89d-42d7-80a9-d431eec5e93e": -2.8756488,
        "35f254a3-8765-4db0-b400-e25751137a15": 17.979799556168015,
        "d5bf54d2-8fc5-4687-8258-7253fb830e33": 1.7571076995476513,
        "30865b43-55bc-4b19-adea-02cb7eccc5f1": 2.9819304685638155,
        "739fa773-14f5-4dab-a896-a10307ae02cd": 4.033809800213324,
        "4b8b6f15-b35d-4efb-b8ed-737d6e9a5532": -5.38247946993428,
        "5329c64b-0948-4044-ab4a-6ddbaf791aff": 18.18288439740379,
        "d8bbcbb3-1bee-4a21-83b6-136cd45a01ec": 18.098207719471787,
        "eab6f5d1-7656-4335-91b5-c61f8ebf2519": 214.54715890549923,
        "56a98dae-ed25-43c2-9112-6019c8f0d796": 33.41153252212025,
        "d3943757-99e1-436a-aa62-5ee97de8ca52": 35.42109739072973,
        "c3ea1ae7-eb1a-42ae-a6e5-528ea9f3614c": -128.9765855533783,
        "6e565aaa-62ea-49f6-9af5-d98982a49017": 281.8268044318624,
        "6767c869-4c9c-4fd9-941e-21b2a5e91a9a": -78.72523141848819,
        "34ad2ea4-1601-4e0f-b6e5-5c0d960a24b1": 530.9570539220307,
        "e958bbd5-0ccf-4961-aa3d-7ea95b633169": 38.45084609964704,
        "82f4366c-c7ee-46c3-83a0-3d46963847a5": -131.75420911286724,
        "ced8dbac-15a2-4c98-abd7-fb8b0b5596d0": 251.5761008539029,
        "574cb57d-057c-463d-acfc-32d16cfb5728": 464.0989090335566,
        "28f03d5f-94c4-420b-9859-6b0052127f0c": -343.66828095346654,
        "8627dc43-64c1-4374-8b77-8add26043e0c": 41.11855030892955,
        "ad3cc1bb-92c5-4a53-a8d7-02f0db377a7f": -104.06855697135144,
        "88792152-efb0-4d77-91f2-327959d3cc2a": 18.911956950069865,
        "1de035f6-2576-41db-ae64-f6d4a9f6a169": -185.13098971297106,
        "45dcb176-1b6d-4958-8925-9ada4da4bd38": 82.89879308359367,
        "5167031b-cc1d-4249-b144-ab38213b6eff": -106.929026611923,
        "54776ad4-c2d1-4d59-853e-78af6090be51": 321.75145979626797,
        "1a83c37e-2f60-4d57-b6ce-e1840e9eb07a": -261.35837215601674,
        "a1ee0f54-950b-43df-bc66-83a576b4901d": 225.54393999479814,
        "17e56e25-f272-451f-a705-a112443bb16a": 39.055891332518776,
        "35ded22a-763f-4f91-b68d-bc51c787002f": 360.410164618755,
        "317acb3b-42a6-481b-82bb-8a77b26ace88": 0.0009104399999999964,
        "0cc1710d-9bf2-4b21-b3c5-85a9517f979e": 0.0,
        "61a04207-60a6-4567-94d7-7f900a99dc6a": 0.0009104399999999961,
        "10db9e88-f1f0-44cc-a063-6f20ba6e34ff": -145.28848611912866,
        "4880e981-e84a-4844-8afa-1f0b564bafd6": 67.7687924592078,
        "250c7958-87bb-4317-a596-c8e8d070f09f": 112.85162250020095,
        "5344d2cc-fd72-43e8-bc23-7af8e8e875d3": 127.32880791994113,
        "901162b3-511a-4e57-bce8-19b1b82ff510": 310.25416847503834,
        "8581a05e-4953-4f0d-a169-8e4a67682d79": -299.1990347961744,
        "bd1f88d0-c0d7-46bc-8127-604e59352c01": 0.0,
        "94256d26-016c-43af-94b5-f1c0fe13e007": 0.0,
        "5fd8459a-cca6-4c29-b46b-615b94b00a0e": 0.0,
        "9130b5e2-572c-4644-9c97-7a197b1f11c3": -15.566111339615375,
        "400133ed-1625-404d-bf8f-ddf30f95e1db": 305.66189092447763,
        "1146e4f5-f13b-4a7a-a700-981032aca2f6": 12.813405697704079,
        "34933e83-8339-4851-9d17-e268d08f78cd": 284.51270041168505,
        "42df2202-337c-4784-a9ac-1a6b3af9acf2": -56.67859460312869,
        "4f457b3e-5f6f-49be-be94-03bab7c8cd19": -102.61633578538316,
        "2f218b34-4f9a-4fc2-ac5c-4cc7954327ba": 58.48869135543365,
        "50c583dd-f830-4ecc-8df7-c966f5f4cc7d": 390.8884761543123,
        "fbba3cb1-80c8-467c-a010-6fa4e1d39901": 440.8716317533342,
        "f06f5c2d-ede1-487f-9552-0304865b1ab2": 104.56048637028056,
        "e9216c06-e4da-474c-aa7f-a2293854e154": -69.06374245994274,
    },
}


class TestForces(unittest.TestCase):
    def test_equal_steel(self):
        max_forces = get_forces(SteelMaterial, SteelSectionProperties)
        for edge, force in max_forces.items():
            self.assertEqual(force, result["steel"][edge])

    def test_equal_unit(self):
        max_forces = get_forces(UnitMaterial, UnitSectionProperties)
        for edge, force in max_forces.items():
            self.assertEqual(force, result["unit"][edge])

    def test_abs_steel(self):
        max_forces = get_forces(SteelMaterial, SteelSectionProperties)
        for edge, force in max_forces.items():
            result_force = result["steel"][edge]
            diff = abs(result_force - force)
            self.assertLessEqual(diff, 1)

    def test_abs_unit(self):
        max_forces = get_forces(UnitMaterial, UnitSectionProperties)
        for edge, force in max_forces.items():
            result_force = result["unit"][edge]
            diff = abs(result_force - force)
            self.assertLessEqual(diff, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
