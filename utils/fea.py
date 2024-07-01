import math

from PyNite import FEModel3D

from search.config import SteelMaterial, SteelSectionProperties
from search.models import Edge, Node


def generate_FEA_truss(nodes: list[Node], edges: list[Edge]) -> FEModel3D:
    truss = FEModel3D()
    truss.add_material(SteelMaterial.name, SteelMaterial.e, SteelMaterial.g, SteelMaterial.nu, SteelMaterial.rho)

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
            SteelMaterial.name,
            SteelSectionProperties.iy,
            SteelSectionProperties.iz,
            SteelSectionProperties.j,
            SteelSectionProperties.a,
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

    for member in truss.Members.values():
        # 110g per m for d=0,2m beam = 1.08N
        # 275g per m for d=0,5m beam = 2.7N
        self_weight = 1.08
        truss.add_member_dist_load(member.name, "FY", self_weight, self_weight)

    return truss

class ForceType:
    TENSION = "TENSION"
    COMPRESSION = "COMPRESSION"

def get_euler_load(l: float, force_type: ForceType) -> float:
    g = 9.81  # gravitational acceleration
    if(ForceType.TENSION == force_type):
        return 700 * g
    
    w = 35 # load-bearing capacity for a beam with 1m length in kg
    return (w * g) / math.pow(l, 2)
