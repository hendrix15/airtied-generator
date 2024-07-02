import math
import unittest

from PyNite import FEModel3D

from utils.parser import read_json

# 110g per m for d=0,2m beam = 1.08N
# 275g per m for d=0,5m beam = 2.7N


class UnitMaterial:
    """Material used for Finite Element Analysis"""

    name = "Unit"
    e = 1
    g = 1
    nu = 1
    rho = 1


class UnitSectionProperties:
    """Section Properties used for Finite Element Analysis"""

    iy = 1
    iz = 1
    j = 1
    a = 1


class TestMaterial:
    """Material used for Finite Element Analysis"""

    name = "Test"
    e = 1
    g = 1
    nu = 1
    rho = 1 / (math.pi * math.pow((0.2 / 2), 2) * 1) * 0.11  # kg per m^3


class TestSectionProperties:
    """Section Properties used for Finite Element Analysis"""

    iy = 1
    iz = 1
    j = 1
    a = math.pi * math.pow((0.2 / 2), 2)  # m^2


class RigidMaterial:
    """Material used for Finite Element Analysis"""

    name = "Rigid"
    e = 99999999  # (ksi) Modulus of elasticity
    g = 100  # (ksi) Shear modulus
    nu = 0.3  # Poisson's ratio
    rho = 1  # (kci) Density


class RigidSectionProperties:
    """Section Properties used for Finite Element Analysis"""

    iy = 100  # (in**4) Weak axis moment of inertia
    iz = 100  # (in**4) Strong axis moment of inertia
    j = 100  # (in**4) Torsional constant
    a = 100  # (in**2) Cross-sectional area


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


class PolycarbonateMaterial:
    """Material used for Finite Element Analysis"""

    name = "Polycarbonate"
    e = 2.2  # (GPa) Modulus of elasticity
    g = 0.7  # # GPa Shear modulus
    nu = 0.36  # Poisson's ratio
    rho = 1210  # kg per cubic metre Density


class PolycarbonateSectionProperties:
    """Section Properties used for Finite Element Analysis"""

    iy = 1  # (m**4) Weak axis moment of inertia
    iz = 1  # (m**4) Strong axis moment of inertia
    j = 1  # (m**4) Torsional constant
    a = 0.0049  # (m**2) Cross-sectional area


def get_forces(
    material: type[
        SteelMaterial
        | UnitMaterial
        | RigidMaterial
        | PolycarbonateMaterial
        | TestMaterial
    ],
    section_properties: type[
        SteelSectionProperties
        | UnitSectionProperties
        | RigidSectionProperties
        | PolycarbonateSectionProperties
        | TestSectionProperties
    ],
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

    # for member in truss.Members.values():
    #     # 110g per m for d=0,2m beam = 1.08N
    #     # 275g per m for d=0,5m beam = 2.7N
    #     self_weight = 1.08
    #     truss.add_member_dist_load(member.name, "FY", self_weight, self_weight)
    truss.add_member_self_weight("FY", 1)
    truss.analyze(check_statics=True)
    max_forces = {member.name: member.max_axial() for member in truss.Members.values()}
    return max_forces


result = {
    "unit": {
        "e435af60-22aa-4fa3-a8cc-e879dbf49dbf": -28.10865738557362,
        "9b094159-9b53-4b7a-b3a8-30146783948f": 24.23519808417309,
        "a376e469-f923-4c1e-999b-ceb5ad2cbc77": -16.576392632633265,
        "693ab2bd-d80c-460a-b7a5-aef24f545903": -39.7976915,
        "03e060e1-ab12-42c7-bd6f-bd370f66b296": 2.824986,
        "985914c5-7cc7-4bae-9c30-060ed6d3dbcb": -64.09262215815272,
        "b59b3ad1-5fa0-4bb3-8b15-85f1b775fcd4": 62.46527322422737,
        "207b968c-75b0-402b-b1d7-0ad4c717ce66": -18.832889728790313,
        "7960a176-f617-4183-811b-9f612f676220": 37.59633549432289,
        "e3c9863d-6ae7-4d8d-b6d0-4d5c80baff97": -7.146805620873829,
        "54bfbac9-1abd-4bc7-8774-3cd7924ba98d": 24.708037,
        "937139e7-313e-4b06-8c57-ad03708a6b99": 59.8421955,
        "0261b51b-7041-4caf-b79e-4c8fa7c9d06f": 32.57417999005772,
        "9aa05d9d-4dea-43c4-8b31-33ef04834bb9": -57.51322180044898,
        "0118da7f-6660-4701-93bf-8c1f4ee7d200": -37.226842579881186,
        "19135b15-691f-4213-af83-0b07baa56a07": -288.2335195457022,
        "393f0ecf-2844-4782-875b-d16ae5a461ae": 6.0211125,
        "25e8fcfa-ab27-4083-81d5-5f4d7f9d21ba": 1.1239999999999997,
        "967ec194-88c3-44f5-b134-0dc3be36e6e7": -10.887945,
        "d395c6cc-3ade-454e-82d0-ba2b620bf7df": 58.011945,
        "badaa4fe-c384-47f0-b4b2-8cbe2ba2f684": -31.0881585,
        "7bcdea3f-c825-4a41-ace2-2789c65302d4": -1.0762134999999997,
        "f5cfc8c5-8c4a-4d2b-8811-2417a84fcc5e": 51.593854,
        "1e09c89d-451f-4d05-bd00-324c86c2dbaa": -8.985439,
        "9b61e11a-185c-4f75-93dd-2cfe6c79c66c": -9.997384,
        "fa073afe-7035-489e-9f5b-84f4884701d1": -0.5973259999999998,
        "be9d13fb-0edc-4db8-884d-e6b48c3dcc49": -11.998818,
        "1842ddbf-3427-4dac-ae4e-62666ccdf7d5": -85.290781,
        "4705cd5f-604c-442b-8bd1-3ba686a5b735": -66.0339865,
        "8860a365-7064-4a33-aa35-b5a5c049864b": -49.3670235,
        "d935c972-96d2-444f-8eb3-06b851507802": -340.2349071609005,
        "549c0819-ad34-4a2b-9a73-f20ac3b4633d": 17.3348135,
        "23c3ef17-b67c-4d43-b00d-06b9beb87a71": -73.7577525,
        "b2d264b4-2d58-4851-a55c-b18384a0715a": -22.7696975,
        "481e5dc0-1e9d-4031-a3fd-fba5d4875b90": 20.962418440948575,
        "284dd3ed-51ae-495c-8944-ac8c64b18c5c": -5.483700854460632,
        "e78feb88-85fe-4996-87ea-e56b58469374": -30.53924206047615,
        "74123fff-52b0-40af-b086-99114521fa0d": 24.57391860728212,
        "f73c39f8-1e16-41e0-b9cf-c49af0de7e9e": -35.935164225426576,
        "6270615a-7635-48eb-89ff-68bf1542c243": -19.055631432450127,
        "ae25b293-1ec2-4ead-a42a-b7c28fb8c614": 77.39536366949986,
        "3410f54f-ee78-47f0-a847-33de66c65491": -27.766013318744807,
        "c48630b6-98a9-493e-bc36-6aa5c4c51090": -14.057752289985002,
        "336c2db5-ee02-46fd-8f3f-b4dfb7839f17": 13.0358415,
        "8083b0b6-061b-4bc5-bfd2-c10cede65dbf": 0.03921099999999989,
        "fe7b3fab-80c3-4163-aa4e-ad09f327861d": 42.2415195,
        "a22e925d-1243-430c-a995-f8bdd703bc49": 0.05359600000000022,
        "cb769ace-b89d-42d7-80a9-d431eec5e93e": 0.1151399999999998,
        "35f254a3-8765-4db0-b400-e25751137a15": 16.647962552008078,
        "d5bf54d2-8fc5-4687-8258-7253fb830e33": 1.6269515736602855,
        "30865b43-55bc-4b19-adea-02cb7eccc5f1": 2.7610467301503334,
        "739fa773-14f5-4dab-a896-a10307ae02cd": 3.552032649499154,
        "4b8b6f15-b35d-4efb-b8ed-737d6e9a5532": -6.12844023462185,
        "5329c64b-0948-4044-ab4a-6ddbaf791aff": 18.364880686710045,
        "d8bbcbb3-1bee-4a21-83b6-136cd45a01ec": 18.216680101141343,
        "eab6f5d1-7656-4335-91b5-c61f8ebf2519": 232.68305478473343,
        "56a98dae-ed25-43c2-9112-6019c8f0d796": 43.0885147516587,
        "d3943757-99e1-436a-aa62-5ee97de8ca52": 36.25137473776697,
        "c3ea1ae7-eb1a-42ae-a6e5-528ea9f3614c": -128.89278888877092,
        "6e565aaa-62ea-49f6-9af5-d98982a49017": 290.7904296854714,
        "6767c869-4c9c-4fd9-941e-21b2a5e91a9a": -85.8183335225375,
        "34ad2ea4-1601-4e0f-b6e5-5c0d960a24b1": 571.9650268906533,
        "e958bbd5-0ccf-4961-aa3d-7ea95b633169": 45.15597938845758,
        "82f4366c-c7ee-46c3-83a0-3d46963847a5": -139.52494836059418,
        "ced8dbac-15a2-4c98-abd7-fb8b0b5596d0": 294.89365901787505,
        "574cb57d-057c-463d-acfc-32d16cfb5728": 485.6582366301276,
        "28f03d5f-94c4-420b-9859-6b0052127f0c": -375.83621548526503,
        "8627dc43-64c1-4374-8b77-8add26043e0c": 58.84516750201997,
        "ad3cc1bb-92c5-4a53-a8d7-02f0db377a7f": -132.05019570861842,
        "88792152-efb0-4d77-91f2-327959d3cc2a": 19.262821967416393,
        "1de035f6-2576-41db-ae64-f6d4a9f6a169": -205.8535226125904,
        "45dcb176-1b6d-4958-8925-9ada4da4bd38": 101.07923024035381,
        "5167031b-cc1d-4249-b144-ab38213b6eff": -128.4270382792258,
        "54776ad4-c2d1-4d59-853e-78af6090be51": 342.0911101798969,
        "1a83c37e-2f60-4d57-b6ce-e1840e9eb07a": -283.82557804416683,
        "a1ee0f54-950b-43df-bc66-83a576b4901d": 250.1080098552006,
        "17e56e25-f272-451f-a705-a112443bb16a": 33.5831428041946,
        "35ded22a-763f-4f91-b68d-bc51c787002f": 359.7091193660992,
        "317acb3b-42a6-481b-82bb-8a77b26ace88": 0.0008429999999999965,
        "0cc1710d-9bf2-4b21-b3c5-85a9517f979e": 0.0,
        "61a04207-60a6-4567-94d7-7f900a99dc6a": 0.0008429999999999964,
        "10db9e88-f1f0-44cc-a063-6f20ba6e34ff": -158.94542952976144,
        "4880e981-e84a-4844-8afa-1f0b564bafd6": 86.72461018921108,
        "250c7958-87bb-4317-a596-c8e8d070f09f": 110.7529769202062,
        "5344d2cc-fd72-43e8-bc23-7af8e8e875d3": 139.36194547749048,
        "901162b3-511a-4e57-bce8-19b1b82ff510": 348.353007337288,
        "8581a05e-4953-4f0d-a169-8e4a67682d79": -322.6353134368359,
        "bd1f88d0-c0d7-46bc-8127-604e59352c01": 0.0,
        "94256d26-016c-43af-94b5-f1c0fe13e007": 0.0,
        "5fd8459a-cca6-4c29-b46b-615b94b00a0e": 0.0,
        "9130b5e2-572c-4644-9c97-7a197b1f11c3": -23.10336010997214,
        "400133ed-1625-404d-bf8f-ddf30f95e1db": 320.03987101344495,
        "1146e4f5-f13b-4a7a-a700-981032aca2f6": 2.756658692380942,
        "34933e83-8339-4851-9d17-e268d08f78cd": 283.8249377014558,
        "42df2202-337c-4784-a9ac-1a6b3af9acf2": -49.49553775122217,
        "4f457b3e-5f6f-49be-be94-03bab7c8cd19": -117.92049532578662,
        "2f218b34-4f9a-4fc2-ac5c-4cc7954327ba": 53.562939501169105,
        "50c583dd-f830-4ecc-8df7-c966f5f4cc7d": 391.558819752364,
        "fbba3cb1-80c8-467c-a010-6fa4e1d39901": 439.94719086211677,
        "f06f5c2d-ede1-487f-9552-0304865b1ab2": 104.82671954265422,
        "e9216c06-e4da-474c-aa7f-a2293854e154": -67.08693703252763,
    },
    "steel": {
        "e435af60-22aa-4fa3-a8cc-e879dbf49dbf": 1177.8511223966934,
        "9b094159-9b53-4b7a-b3a8-30146783948f": 547.6547139221466,
        "a376e469-f923-4c1e-999b-ceb5ad2cbc77": 49.88840990594925,
        "693ab2bd-d80c-460a-b7a5-aef24f545903": 71.7653505922265,
        "03e060e1-ab12-42c7-bd6f-bd370f66b296": 27.476713521823996,
        "985914c5-7cc7-4bae-9c30-060ed6d3dbcb": -545.9963185304599,
        "b59b3ad1-5fa0-4bb3-8b15-85f1b775fcd4": 607.3474717140189,
        "207b968c-75b0-402b-b1d7-0ad4c717ce66": 952.5127722105424,
        "7960a176-f617-4183-811b-9f612f676220": -433.07865310282875,
        "e3c9863d-6ae7-4d8d-b6d0-4d5c80baff97": -274.3209072311662,
        "54bfbac9-1abd-4bc7-8774-3cd7924ba98d": -772.822913830767,
        "937139e7-313e-4b06-8c57-ad03708a6b99": 67.51844149310952,
        "0261b51b-7041-4caf-b79e-4c8fa7c9d06f": 1091.2873990066662,
        "9aa05d9d-4dea-43c4-8b31-33ef04834bb9": -1595.91247901798,
        "0118da7f-6660-4701-93bf-8c1f4ee7d200": -977.4518686001071,
        "19135b15-691f-4213-af83-0b07baa56a07": -782.7273296563112,
        "393f0ecf-2844-4782-875b-d16ae5a461ae": 132.0022305562625,
        "25e8fcfa-ab27-4083-81d5-5f4d7f9d21ba": -59.24042008400002,
        "967ec194-88c3-44f5-b134-0dc3be36e6e7": -59.69891348800501,
        "d395c6cc-3ade-454e-82d0-ba2b620bf7df": 240.458493404005,
        "badaa4fe-c384-47f0-b4b2-8cbe2ba2f684": -153.0001412098765,
        "7bcdea3f-c825-4a41-ace2-2789c65302d4": -212.5416478058715,
        "f5cfc8c5-8c4a-4d2b-8811-2417a84fcc5e": 693.3726282338611,
        "1e09c89d-451f-4d05-bd00-324c86c2dbaa": 83.750759686749,
        "9b61e11a-185c-4f75-93dd-2cfe6c79c66c": 147.292266282744,
        "fa073afe-7035-489e-9f5b-84f4884701d1": 783.456121637866,
        "be9d13fb-0edc-4db8-884d-e6b48c3dcc49": -63.954630455962,
        "1842ddbf-3427-4dac-ae4e-62666ccdf7d5": -1388.777544286729,
        "4705cd5f-604c-442b-8bd1-3ba686a5b735": -15.526928050928497,
        "8860a365-7064-4a33-aa35-b5a5c049864b": -1303.7040142201615,
        "d935c972-96d2-444f-8eb3-06b851507802": 876.9165267264502,
        "549c0819-ad34-4a2b-9a73-f20ac3b4633d": 0.452402140771504,
        "23c3ef17-b67c-4d43-b00d-06b9beb87a71": -710.7016424540225,
        "b2d264b4-2d58-4851-a55c-b18384a0715a": -775.1601358580275,
        "481e5dc0-1e9d-4031-a3fd-fba5d4875b90": 804.6153693739179,
        "284dd3ed-51ae-495c-8944-ac8c64b18c5c": -210.4847778407056,
        "e78feb88-85fe-4996-87ea-e56b58469374": -345.26424730378443,
        "74123fff-52b0-40af-b086-99114521fa0d": 508.90078860010976,
        "f73c39f8-1e16-41e0-b9cf-c49af0de7e9e": -397.31903007242704,
        "6270615a-7635-48eb-89ff-68bf1542c243": -109.30108548823166,
        "ae25b293-1ec2-4ead-a42a-b7c28fb8c614": 2127.9347856554687,
        "3410f54f-ee78-47f0-a847-33de66c65491": -749.5976012959087,
        "c48630b6-98a9-493e-bc36-6aa5c4c51090": -353.94842988410807,
        "336c2db5-ee02-46fd-8f3f-b4dfb7839f17": 159.7594387061235,
        "8083b0b6-061b-4bc5-bfd2-c10cede65dbf": 1.5050636135989957,
        "fe7b3fab-80c3-4163-aa4e-ad09f327861d": 73.27041420582549,
        "a22e925d-1243-430c-a995-f8bdd703bc49": 258.057213267564,
        "cb769ace-b89d-42d7-80a9-d431eec5e93e": -91.58049974574001,
        "35f254a3-8765-4db0-b400-e25751137a15": 639.0105500391753,
        "d5bf54d2-8fc5-4687-8258-7253fb830e33": 62.448435760244195,
        "30865b43-55bc-4b19-adea-02cb7eccc5f1": 105.97921422550074,
        "739fa773-14f5-4dab-a896-a10307ae02cd": 332.0521518521715,
        "4b8b6f15-b35d-4efb-b8ed-737d6e9a5532": 462.31527808560315,
        "5329c64b-0948-4044-ab4a-6ddbaf791aff": -57.897842483587795,
        "d8bbcbb3-1bee-4a21-83b6-136cd45a01ec": -28.762535443786774,
        "eab6f5d1-7656-4335-91b5-c61f8ebf2519": -1332.0229459664097,
        "56a98dae-ed25-43c2-9112-6019c8f0d796": -766.8583636539684,
        "d3943757-99e1-436a-aa62-5ee97de8ca52": -555.8773193159112,
        "c3ea1ae7-eb1a-42ae-a6e5-528ea9f3614c": 159.16481175011384,
        "6e565aaa-62ea-49f6-9af5-d98982a49017": -887.2909764827087,
        "6767c869-4c9c-4fd9-941e-21b2a5e91a9a": 97.50818013532444,
        "34ad2ea4-1601-4e0f-b6e5-5c0d960a24b1": -2155.1843441728624,
        "e958bbd5-0ccf-4961-aa3d-7ea95b633169": 467.7493707203819,
        "82f4366c-c7ee-46c3-83a0-3d46963847a5": 310.4325976656699,
        "ced8dbac-15a2-4c98-abd7-fb8b0b5596d0": -2937.334354890955,
        "574cb57d-057c-463d-acfc-32d16cfb5728": -1302.621397506663,
        "28f03d5f-94c4-420b-9859-6b0052127f0c": 1199.509546918557,
        "8627dc43-64c1-4374-8b77-8add26043e0c": -891.8442431264959,
        "ad3cc1bb-92c5-4a53-a8d7-02f0db377a7f": 1616.9343429047894,
        "88792152-efb0-4d77-91f2-327959d3cc2a": 732.7334196841416,
        "1de035f6-2576-41db-ae64-f6d4a9f6a169": 768.9225079841235,
        "45dcb176-1b6d-4958-8925-9ada4da4bd38": -481.62443904689644,
        "5167031b-cc1d-4249-b144-ab38213b6eff": 109.81604167329905,
        "54776ad4-c2d1-4d59-853e-78af6090be51": -1192.2096386511107,
        "1a83c37e-2f60-4d57-b6ce-e1840e9eb07a": -688.2800355450233,
        "a1ee0f54-950b-43df-bc66-83a576b4901d": -1215.272889713072,
        "17e56e25-f272-451f-a705-a112443bb16a": -168.33472833390186,
        "35ded22a-763f-4f91-b68d-bc51c787002f": -107.29427340866883,
        "317acb3b-42a6-481b-82bb-8a77b26ace88": 0.032357466686999875,
        "0cc1710d-9bf2-4b21-b3c5-85a9517f979e": 0.0,
        "61a04207-60a6-4567-94d7-7f900a99dc6a": 0.03235746668699986,
        "10db9e88-f1f0-44cc-a063-6f20ba6e34ff": -662.6419007098211,
        "4880e981-e84a-4844-8afa-1f0b564bafd6": 338.82817739742524,
        "250c7958-87bb-4317-a596-c8e8d070f09f": -380.39094252375173,
        "5344d2cc-fd72-43e8-bc23-7af8e8e875d3": -2461.147605350438,
        "901162b3-511a-4e57-bce8-19b1b82ff510": -1748.120639585827,
        "8581a05e-4953-4f0d-a169-8e4a67682d79": 2047.4731978362786,
        "bd1f88d0-c0d7-46bc-8127-604e59352c01": 0.0,
        "94256d26-016c-43af-94b5-f1c0fe13e007": 0.0,
        "5fd8459a-cca6-4c29-b46b-615b94b00a0e": 0.0,
        "9130b5e2-572c-4644-9c97-7a197b1f11c3": 1001.1279758825607,
        "400133ed-1625-404d-bf8f-ddf30f95e1db": -353.2759744696081,
        "1146e4f5-f13b-4a7a-a700-981032aca2f6": -2037.8225949616146,
        "34933e83-8339-4851-9d17-e268d08f78cd": -760.6733381917376,
        "42df2202-337c-4784-a9ac-1a6b3af9acf2": -72.35994266584184,
        "4f457b3e-5f6f-49be-be94-03bab7c8cd19": -972.527264821172,
        "2f218b34-4f9a-4fc2-ac5c-4cc7954327ba": 1992.1137106119631,
        "50c583dd-f830-4ecc-8df7-c966f5f4cc7d": 719.4564807772779,
        "fbba3cb1-80c8-467c-a010-6fa4e1d39901": -510.0328768184567,
        "f06f5c2d-ede1-487f-9552-0304865b1ab2": -795.5496149633531,
        "e9216c06-e4da-474c-aa7f-a2293854e154": 442.8768810324525,
    },
}


class TestForces(unittest.TestCase):
    def test_abs_unit(self):
        max_forces = get_forces(UnitMaterial, UnitSectionProperties)
        for edge, force in max_forces.items():
            result_force = result["unit"][edge]
            diff = abs(result_force - force)
            self.assertLessEqual(diff, 1)

    def test_abs_steel(self):
        max_forces = get_forces(SteelMaterial, SteelSectionProperties)
        for edge, force in max_forces.items():
            result_force = result["steel"][edge]
            diff = abs(result_force - force)
            self.assertLessEqual(diff, 1)

    # def test_equal_unit_test(self):
    #     unit_max_forces = get_forces(UnitMaterial, UnitSectionProperties)
    #     test_max_forces = get_forces(TestMaterial, TestSectionProperties)
    #     for edge, force in unit_max_forces.items():
    #         result_force = test_max_forces[edge]
    #         diff = abs(result_force - force)
    #         self.assertLessEqual(diff, 1)

    # def test_abs_unit_rigid(self):
    #     unit_max_forces = get_forces(UnitMaterial, UnitSectionProperties)
    #     rigid_max_forces = get_forces(RigidMaterial, RigidSectionProperties)
    #     for edge, force in unit_max_forces.items():
    #         result_force = rigid_max_forces[edge]
    #         diff = abs(result_force - force)
    #         self.assertLessEqual(diff, 1)

    # def test_abs_unit_steel(self):
    #     unit_max_forces = get_forces(UnitMaterial, UnitSectionProperties)
    #     steel_max_forces = get_forces(SteelMaterial, SteelSectionProperties)
    #     for edge, force in unit_max_forces.items():
    #         result_force = steel_max_forces[edge]
    #         diff = abs(result_force - force)
    #         self.assertLessEqual(diff, 1)

    # def test_abs_unit_polycarbonate(self):
    #     unit_max_forces = get_forces(UnitMaterial, UnitSectionProperties)
    #     polycarbonate_max_forces = get_forces(
    #         PolycarbonateMaterial, PolycarbonateSectionProperties
    #     )
    #     for edge, force in unit_max_forces.items():
    #         result_force = polycarbonate_max_forces[edge]
    #         diff = abs(result_force - force)
    #         self.assertLessEqual(diff, 1)

    # def test_abs_steel_polycarbonate(self):
    #     steel_max_forces = get_forces(SteelMaterial, SteelSectionProperties)
    #     polycarbonate_max_forces = get_forces(
    #         PolycarbonateMaterial, PolycarbonateSectionProperties
    #     )
    #     for edge, force in steel_max_forces.items():
    #         result_force = polycarbonate_max_forces[edge]
    #         diff = abs(result_force - force)
    #         self.assertLessEqual(diff, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
