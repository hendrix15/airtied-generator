import numpy as np
import openseespy.opensees as ops

from fea.utils import Material, SectionProperties
from search.models import Edge, Node


def fea_opensees(nodes: list[Node], edges: list[Edge]) -> dict:
    node_mapping = {node.id: i for i, node in enumerate(nodes)}
    edge_mapping = {edge.id: i for i, edge in enumerate(edges)}

    material = Material()
    section_properties = SectionProperties()

    ops.wipe()
    ops.model("basic", "-ndm", 3, "-ndf", 6)

    ops.timeSeries("Constant", 1)
    ops.pattern("Plain", 1, 1)

    for node in nodes:
        ops.node(node_mapping[node.id], node.vec.x, node.vec.y, node.vec.z)
        if node.r_support and node.t_support:
            ops.fix(
                node_mapping[node.id],
                int(node.t_support.x),
                int(node.t_support.y),
                int(node.t_support.z),
                int(node.r_support.x),
                int(node.r_support.y),
                int(node.r_support.z),
            )
        if node.load:
            ops.load(
                node_mapping[node.id],
                node.load.x,
                node.load.y,
                node.load.z,
                0,
                0,
                0,
            )

    # Transformation of local coordinate system
    ops.geomTransf("Linear", 1, 0, 0, 1)
    ops.geomTransf("Linear", 2, 1, 0, 0)

    for edge in edges:
        # Select transformation
        transform = (
            2 if edge.u.vec.x == edge.v.vec.x and edge.u.vec.y == edge.v.vec.y else 1
        )
        ops.element(
            "elasticBeamColumn",
            edge_mapping[edge.id],
            node_mapping[edge.u.id],
            node_mapping[edge.v.id],
            section_properties.a,
            material.e,
            material.g,
            section_properties.j,
            section_properties.iz,
            section_properties.iy,
            transform,
        )

    # Add self weight of the beams
    for edge in edges:
        b = [0, -material.rho * section_properties.a, 0]
        wx = np.dot(ops.eleResponse(edge_mapping[edge.id], "xaxis"), b)  # x'*b
        wy = np.dot(ops.eleResponse(edge_mapping[edge.id], "yaxis"), b)  # y'*b
        wz = np.dot(ops.eleResponse(edge_mapping[edge.id], "zaxis"), b)  # z'*b
        ops.eleLoad("-ele", edge_mapping[edge.id], "-type", "-beamUniform", wy, wz, wx)

    ops.system("BandSPD")
    ops.numberer("RCM")
    ops.constraints("Plain")
    ops.integrator("LoadControl", 1.0)
    ops.algorithm("Linear")
    ops.analysis("Static")

    result = ops.analyze(1)
    if result == -3:  # Ax=b failed
        raise Exception("Singularity Error")

    max_forces = {
        edge.id: ops.basicForce(edge_mapping[edge.id])[0] * -1 for edge in edges
    }
    return max_forces
