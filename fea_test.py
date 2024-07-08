import numpy as np
from PyNite import FEModel3D

from fea.openseespy import fea_opensees
from fea.pynite import fea_pynite
from fea.utils import Material, SectionProperties
from search.models import Edge, Node
from utils.parser import read_json


def pynite(nodes: list[Node], edges: list[Edge], material: bool) -> dict:
    truss = FEModel3D()
    if material:
        truss.add_material(
            Material.name, Material.e, Material.g, Material.nu, Material.rho
        )
    else:
        truss.add_material(Material.name, 1, 1, 1, 1)

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
        if material:
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
        else:
            truss.add_member(
                edge.id,
                edge.u.id,
                edge.v.id,
                Material.name,
                1,
                1,
                1,
                1,
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
    # truss.add_member_self_weight("FY", -1)

    truss.analyze(check_statics=True, sparse=False)
    max_forces = {member.name: member.max_axial() for member in truss.Members.values()}
    if any(np.isnan(max_force) for max_force in max_forces.values()):
        raise Exception("At least one of the axial forces is nan")
    return max_forces


def test_pynite() -> None:
    for file_name in [
        "dino.json",
        "triangle.json",
        "simple_pyramid.json",
        "complex_pyramid.json",
    ]:
        nodes, edges = read_json(f"output/{file_name}")
        pynite_no_material = pynite(nodes, edges, True)
        pynite_material = pynite(nodes, edges, True)
        for edge, force in pynite_no_material.items():
            assert pynite_material[edge] == force


def test_opensees() -> None:
    for file_name in [
        "dino.json",
        "triangle.json",
        "simple_pyramid.json",
        "complex_pyramid.json",
    ]:
        nodes, edges = read_json(f"output/{file_name}")
        opensees_max_forces = fea_opensees(nodes, edges)


def fea_comparison() -> None:
    for file_name in [
        "dino.json",
        "triangle.json",
        "simple_pyramid.json",
        "complex_pyramid.json",
    ]:
        nodes, edges = read_json(f"output/{file_name}")
        pynite_max_forces = fea_pynite(nodes, edges)
        opensees_max_forces = fea_opensees(nodes, edges)
        print("PyNite \n")
        for edge, force in pynite_max_forces.items():
            print(f"{edge} - {force}")
        print("\n \n")
        print("Opensees \n")
        for edge, force in opensees_max_forces.items():
            print(f"{edge} - {force}")
        print("\n")
        max_abs = max(
            abs(opensees_max_forces[edge] - force)
            for edge, force in pynite_max_forces.items()
        )
        print(f"Max diff: {max_abs}")
        print("\n \n")


if __name__ == "__main__":
    fea_comparison()
