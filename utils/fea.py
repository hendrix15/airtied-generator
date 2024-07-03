import math

import numpy as np
import openseespy.opensees as ops
from PyNite import FEModel3D

from search.models import Edge, Node

# 110g per m for d=0,2m beam = 1.08N
# 275g per m for d=0,5m beam = 2.7N


class Material:
    """Material used for Finite Element Analysis"""

    name = "Steel"
    e = 199.95  # (GPa) Modulus of elasticity
    g = 78.60  # (GPa) Shear modulus
    nu = 0.30  # Poisson's ratio
    rho = 1 / (math.pi * math.pow((0.2 / 2), 2) * 1) * 0.11  # (N per m^3) Density


class SectionProperties:
    """Section Properties used for Finite Element Analysis"""

    iy = 0.0000072  # (m**4) Weak axis moment of inertia
    iz = 0.000085  # (m**4) Strong axis moment of inertia
    j = 1.249e-7  # (m**4) Torsional constant
    a = math.pi * math.pow((0.2 / 2), 2)  # (m^2) Cross-sectional area


class ForceType:
    TENSION = "TENSION"
    COMPRESSION = "COMPRESSION"


def fea_pynite(nodes: list[Node], edges: list[Edge]) -> dict:
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

    truss.analyze(check_statics=True, sparse=False)
    max_forces = {member.name: member.max_axial() for member in truss.Members.values()}
    if any(np.isnan(max_force) for max_force in max_forces.values()):
        raise Exception("At least one of the axial forces is nan")
    return max_forces


def fea_opensees(nodes: list[Node], edges: list[Edge], truss: bool = False) -> dict:
    node_mapping = {node.id: i for i, node in enumerate(nodes)}
    edge_mapping = {edge.id: i for i, edge in enumerate(edges)}

    ops.wipe()

    if truss:
        ops.model("basic", "-ndm", 3, "-ndf", 3)
    else:
        ops.model("basic", "-ndm", 3, "-ndf", 6)

    ops.timeSeries("Constant", 1)
    ops.pattern("Plain", 1, 1)

    for node in nodes:
        ops.node(node_mapping[node.id], node.vec.x, node.vec.y, node.vec.z)

    if truss:
        # Reinforced steel
        ops.uniaxialMaterial("Steel01", 1, 60.0, 30000.0, 0.01)
    else:
        # Transformation of local coordinate system
        ops.geomTransf("Linear", 1, 0, 0, 1)
        ops.geomTransf("Linear", 2, 1, 0, 0)
        # Calculate self weight of the beams
        b = [0, -Material.rho * SectionProperties.a, 0]
        wx = np.dot(ops.eleResponse(1, "xaxis"), b)  # x'*b
        wy = np.dot(ops.eleResponse(1, "yaxis"), b)  # y'*b
        wz = np.dot(ops.eleResponse(1, "zaxis"), b)  # z'*b

    for edge in edges:
        if truss:
            ops.element(
                "Truss",
                edge_mapping[edge.id],
                node_mapping[edge.u.id],
                node_mapping[edge.v.id],
                SectionProperties.a,
                1,
            )
        else:
            # Select transformation
            transform = (
                2
                if edge.u.vec.x == edge.v.vec.x and edge.u.vec.y == edge.v.vec.y
                else 1
            )
            ops.element(
                "elasticBeamColumn",
                edge_mapping[edge.id],
                node_mapping[edge.u.id],
                node_mapping[edge.v.id],
                SectionProperties.a,
                Material.e,
                Material.g,
                SectionProperties.j,
                SectionProperties.iz,
                SectionProperties.iy,
                transform,
            )
            # Add self weight
            ops.eleLoad(
                "-ele", edge_mapping[edge.id], "-type", "-beamUniform", wy, wz, wx
            )

    for node in nodes:
        if node.r_support and node.t_support:
            if truss:
                ops.fix(
                    node_mapping[node.id],
                    int(node.t_support.x),
                    int(node.t_support.y),
                    int(node.t_support.z),
                )
            else:
                ops.fix(
                    node_mapping[node.id],
                    int(node.t_support.x),
                    int(node.t_support.y),
                    int(node.t_support.z),
                    int(node.r_support.x),
                    int(node.r_support.y),
                    int(node.r_support.z),
                )

    for node in nodes:
        if node.load:
            if truss:
                ops.load(node_mapping[node.id], node.load.x, node.load.y, node.load.z)
            else:
                ops.load(
                    node_mapping[node.id],
                    node.load.x,
                    node.load.y,
                    node.load.z,
                    0,
                    0,
                    0,
                )

    ops.system("BandSPD")
    ops.numberer("RCM")
    ops.constraints("Plain")
    ops.integrator("LoadControl", 1.0)
    ops.algorithm("Linear")
    ops.analysis("Static")

    result = ops.analyze(1)
    if result == -3:  # Ax=b failed
        for nd in ops.getNodeTags():
            print(f"Node {nd}: {ops.nodeDOFs(nd)}")

    max_forces = {
        edge.id: ops.basicForce(edge_mapping[edge.id])[0] * -1 for edge in edges
    }
    return max_forces


def get_euler_load(l: float, force_type: ForceType) -> float:
    if force_type == ForceType.COMPRESSION:
        # gravitational acceleration and load-bearing capacity for a beam with 1m length in kg
        return 9.81 * 35 / math.pow(l, 2)
    return 9.81 * 700


def get_compression_tension_edges(edges: list[Edge], max_forces: dict) -> list[dict]:
    force_edges = []
    for edge in edges:
        max_force = max_forces[edge.id]
        force_type = ForceType.COMPRESSION if max_force > 0 else ForceType.TENSION
        euler_load = get_euler_load(l=edge.length(), force_type=force_type)
        if abs(max_force) > euler_load:
            force_edges.append(
                {
                    "id": edge.id,
                    "force_type": force_type,
                    "max_force": max_force,
                    "euler_load": euler_load,
                }
            )
    return force_edges
