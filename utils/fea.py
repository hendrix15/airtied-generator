import math

from PyNite import FEModel3D

from search.config import Material, SectionProperties
from search.models import Edge, Node


def generate_FEA_truss(nodes: list[Node], edges: list[Edge]) -> FEModel3D:
    truss = FEModel3D()
    truss.add_material(Material.name, Material.e, Material.g, Material.nu, Material.rho)

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
            Material.name,
            SectionProperties.iy,
            SectionProperties.iz,
            SectionProperties.j,
            SectionProperties.a,
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

    # Add self weight of the beams
    truss.add_member_self_weight("FY", -1)

    return truss


class ForceType:
    TENSION = "TENSION"
    COMPRESSION = "COMPRESSION"


def get_euler_load(l: float, force_type: ForceType) -> float:
    if force_type == ForceType.COMPRESSION:
        # gravitational acceleration and load-bearing capacity for a beam with 1m length in kg
        return 9.81 * 35 / math.pow(l, 2)
    return 9.81 * 700
