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
    rho = 1 / (math.pi * math.pow((0.2 / 2), 2) * 1) * 0.11 * 9.81  # kg per m^3


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
    truss.add_member_self_weight("FY", -1)
    truss.analyze(check_statics=True)
    max_forces = {member.name: member.max_axial() for member in truss.Members.values()}
    return max_forces


result = {
    "e435af60-22aa-4fa3-a8cc-e879dbf49dbf": -40.694857611373514,
    "9b094159-9b53-4b7a-b3a8-30146783948f": -12.159197813074417,
    "a376e469-f923-4c1e-999b-ceb5ad2cbc77": -5.3400744745871735,
    "693ab2bd-d80c-460a-b7a5-aef24f545903": 0.10112360235000001,
    "03e060e1-ab12-42c7-bd6f-bd370f66b296": -3.30766307615,
    "985914c5-7cc7-4bae-9c30-060ed6d3dbcb": 35.29484932227326,
    "b59b3ad1-5fa0-4bb3-8b15-85f1b775fcd4": -32.062671188262044,
    "207b968c-75b0-402b-b1d7-0ad4c717ce66": -22.528193360013827,
    "7960a176-f617-4183-811b-9f612f676220": 7.536104518633513,
    "e3c9863d-6ae7-4d8d-b6d0-4d5c80baff97": 8.860487532683681,
    "54bfbac9-1abd-4bc7-8774-3cd7924ba98d": 22.185917726699998,
    "937139e7-313e-4b06-8c57-ad03708a6b99": -6.047730585949999,
    "0261b51b-7041-4caf-b79e-4c8fa7c9d06f": -27.780425891138236,
    "9aa05d9d-4dea-43c4-8b31-33ef04834bb9": 47.60727557454051,
    "0118da7f-6660-4701-93bf-8c1f4ee7d200": 26.190601759619145,
    "19135b15-691f-4213-af83-0b07baa56a07": 20.659194044295887,
    "393f0ecf-2844-4782-875b-d16ae5a461ae": -3.6710659387499995,
    "25e8fcfa-ab27-4083-81d5-5f4d7f9d21ba": 1.2588083999999997,
    "967ec194-88c3-44f5-b134-0dc3be36e6e7": 3.3279498005,
    "d395c6cc-3ade-454e-82d0-ba2b620bf7df": -13.694141400500001,
    "badaa4fe-c384-47f0-b4b2-8cbe2ba2f684": 9.601155662650001,
    "7bcdea3f-c825-4a41-ace2-2789c65302d4": 7.168733012150001,
    "f5cfc8c5-8c4a-4d2b-8811-2417a84fcc5e": -23.30633064469375,
    "1e09c89d-451f-4d05-bd00-324c86c2dbaa": -0.2650497248999999,
    "9b61e11a-185c-4f75-93dd-2cfe6c79c66c": -1.0943458244,
    "fa073afe-7035-489e-9f5b-84f4884701d1": -20.4932088616,
    "be9d13fb-0edc-4db8-884d-e6b48c3dcc49": -0.12372450379999998,
    "1842ddbf-3427-4dac-ae4e-62666ccdf7d5": 52.0680525979,
    "4705cd5f-604c-442b-8bd1-3ba686a5b735": 11.62775173035,
    "8860a365-7064-4a33-aa35-b5a5c049864b": 48.98577931615,
    "d935c972-96d2-444f-8eb3-06b851507802": -23.7767548392809,
    "549c0819-ad34-4a2b-9a73-f20ac3b4633d": 0.9325253728500001,
    "23c3ef17-b67c-4d43-b00d-06b9beb87a71": 28.50554990225,
    "b2d264b4-2d58-4851-a55c-b18384a0715a": 26.44969130275,
    "481e5dc0-1e9d-4031-a3fd-fba5d4875b90": -20.272741395057114,
    "284dd3ed-51ae-495c-8944-ac8c64b18c5c": 7.078950877050153,
    "e78feb88-85fe-4996-87ea-e56b58469374": 12.435165478411928,
    "74123fff-52b0-40af-b086-99114521fa0d": -11.080269779559405,
    "f73c39f8-1e16-41e0-b9cf-c49af0de7e9e": 13.97500785778128,
    "6270615a-7635-48eb-89ff-68bf1542c243": 3.3708375066222547,
    "ae25b293-1ec2-4ead-a42a-b7c28fb8c614": -58.47564456595591,
    "3410f54f-ee78-47f0-a847-33de66c65491": 22.279553825462553,
    "c48630b6-98a9-493e-bc36-6aa5c4c51090": 11.11131362154036,
    "336c2db5-ee02-46fd-8f3f-b4dfb7839f17": -4.9173796873499995,
    "8083b0b6-061b-4bc5-bfd2-c10cede65dbf": 0.4798125900999999,
    "fe7b3fab-80c3-4163-aa4e-ad09f327861d": -0.6378138075500001,
    "a22e925d-1243-430c-a995-f8bdd703bc49": -7.9421645564,
    "cb769ace-b89d-42d7-80a9-d431eec5e93e": -7.477314926,
    "35f254a3-8765-4db0-b400-e25751137a15": -15.73865251367217,
    "d5bf54d2-8fc5-4687-8258-7253fb830e33": -0.6909688519332148,
    "30865b43-55bc-4b19-adea-02cb7eccc5f1": -1.901651237508046,
    "739fa773-14f5-4dab-a896-a10307ae02cd": -7.274897754263183,
    "4b8b6f15-b35d-4efb-b8ed-737d6e9a5532": -10.724932272540489,
    "5329c64b-0948-4044-ab4a-6ddbaf791aff": 1.6398419573025527,
    "d8bbcbb3-1bee-4a21-83b6-136cd45a01ec": 0.8498129927885552,
    "eab6f5d1-7656-4335-91b5-c61f8ebf2519": 31.93896918056637,
    "56a98dae-ed25-43c2-9112-6019c8f0d796": 22.30650059129634,
    "d3943757-99e1-436a-aa62-5ee97de8ca52": 16.090207386834187,
    "c3ea1ae7-eb1a-42ae-a6e5-528ea9f3614c": -1.5461412951926232,
    "6e565aaa-62ea-49f6-9af5-d98982a49017": 23.82316143401227,
    "6767c869-4c9c-4fd9-941e-21b2a5e91a9a": 1.244793572364017,
    "34ad2ea4-1601-4e0f-b6e5-5c0d960a24b1": 47.55484039636269,
    "e958bbd5-0ccf-4961-aa3d-7ea95b633169": -21.142677960255753,
    "82f4366c-c7ee-46c3-83a0-3d46963847a5": -2.9511214901996086,
    "ced8dbac-15a2-4c98-abd7-fb8b0b5596d0": 79.21000427979111,
    "574cb57d-057c-463d-acfc-32d16cfb5728": 33.21586743402779,
    "28f03d5f-94c4-420b-9859-6b0052127f0c": -17.711151550870166,
    "8627dc43-64c1-4374-8b77-8add26043e0c": 20.332580638874177,
    "ad3cc1bb-92c5-4a53-a8d7-02f0db377a7f": -36.95319589492132,
    "88792152-efb0-4d77-91f2-327959d3cc2a": -28.280655620885334,
    "1de035f6-2576-41db-ae64-f6d4a9f6a169": -12.99937555930029,
    "45dcb176-1b6d-4958-8925-9ada4da4bd38": 4.488935980870991,
    "5167031b-cc1d-4249-b144-ab38213b6eff": 15.10635589675879,
    "54776ad4-c2d1-4d59-853e-78af6090be51": 28.63354320571033,
    "1a83c37e-2f60-4d57-b6ce-e1840e9eb07a": 39.927734577098995,
    "a1ee0f54-950b-43df-bc66-83a576b4901d": 31.52204650666146,
    "17e56e25-f272-451f-a705-a112443bb16a": 9.495459720506618,
    "35ded22a-763f-4f91-b68d-bc51c787002f": 1.4093776713531865,
    "317acb3b-42a6-481b-82bb-8a77b26ace88": 0.0009096812999999967,
    "0cc1710d-9bf2-4b21-b3c5-85a9517f979e": 0.0,
    "61a04207-60a6-4567-94d7-7f900a99dc6a": 0.0009096812999999965,
    "10db9e88-f1f0-44cc-a063-6f20ba6e34ff": 35.37579183907627,
    "4880e981-e84a-4844-8afa-1f0b564bafd6": -23.068205814870304,
    "250c7958-87bb-4317-a596-c8e8d070f09f": 16.114812887729006,
    "5344d2cc-fd72-43e8-bc23-7af8e8e875d3": 81.59313923230641,
    "901162b3-511a-4e57-bce8-19b1b82ff510": 37.055440989399614,
    "8581a05e-4953-4f0d-a169-8e4a67682d79": -55.59118794722863,
    "bd1f88d0-c0d7-46bc-8127-604e59352c01": 0.0,
    "94256d26-016c-43af-94b5-f1c0fe13e007": 0.0,
    "5fd8459a-cca6-4c29-b46b-615b94b00a0e": 0.0,
    "9130b5e2-572c-4644-9c97-7a197b1f11c3": -30.76556425842783,
    "400133ed-1625-404d-bf8f-ddf30f95e1db": 0.22893817728144417,
    "1146e4f5-f13b-4a7a-a700-981032aca2f6": 80.6497261288742,
    "34933e83-8339-4851-9d17-e268d08f78cd": 27.119459024795095,
    "42df2202-337c-4784-a9ac-1a6b3af9acf2": -2.196870604823998,
    "4f457b3e-5f6f-49be-be94-03bab7c8cd19": 50.72115332443003,
    "2f218b34-4f9a-4fc2-ac5c-4cc7954327ba": -62.92420272070227,
    "50c583dd-f830-4ecc-8df7-c966f5f4cc7d": -16.510629820013257,
    "fbba3cb1-80c8-467c-a010-6fa4e1d39901": 28.922778687821,
    "f06f5c2d-ede1-487f-9552-0304865b1ab2": 37.70479027380497,
    "e9216c06-e4da-474c-aa7f-a2293854e154": -10.347690852266286,
}


class TestForces(unittest.TestCase):
    def test_abs_test(self):
        max_forces = get_forces(TestMaterial, TestSectionProperties)
        for edge, force in max_forces.items():
            result_force = result[edge]
            diff = abs(result_force - force)
            self.assertLessEqual(diff, 1)

    # def test_abs_steel(self):
    #     max_forces = get_forces(SteelMaterial, SteelSectionProperties)
    #     for edge, force in max_forces.items():
    #         result_force = result["steel"][edge]
    #         diff = abs(result_force - force)
    #         self.assertLessEqual(diff, 1)

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
    # max_forces = get_forces(TestMaterial, TestSectionProperties)
    # print(max_forces)
