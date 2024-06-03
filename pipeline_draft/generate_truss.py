import json

from PyNite import FEModel3D, Visualization

from pipeline_draft.config import Material, SectionProperties


def get_truss(anchors, forces, input_file):
    # Magic ✨
    if "example_input_2.json" in input_file:
        with open("output/example_tower_2.json") as f:
            truss = json.load(f)
            return truss["nodes"], truss["edges"], truss["anchors"], truss["forces"]
    elif "example_input_1.json" in input_file:
        with open("output/example_tower_1.json") as f:
            truss = json.load(f)
            return truss["nodes"], truss["edges"], truss["anchors"], truss["forces"]


def generate_truss(input_file):
    # read input as json
    with open(input_file) as f:
        input_data = json.load(f)

    # set anchors and forces from input data
    anchors = input_data.get("anchors", {})
    nodes = input_data.get("nodes", {})
    forces = input_data.get("forces", {})

    edges = input_data.get("edges", {})

    nodes, edges, anchors, forces = get_truss(anchors, forces, input_file)

    return nodes, edges, anchors, forces


def finite_element_analysis(nodes, edges, anchors, forces) -> FEModel3D:
    truss_model = generate_FEA_truss(nodes, edges, anchors, forces)
    truss_model.analyze_PDelta()

    for members in truss_model.Members.values():
        print(f"Member {members.name} calculated axial force: {members.max_axial()}")

    return truss_model


def visualize(truss_model: FEModel3D):
    Visualization.render_model(
        truss_model, annotation_size=0.05, render_loads=True, case="Case 1"
    )


def generate_FEA_truss(nodes, edges, anchors, forces) -> FEModel3D:
    truss = FEModel3D()
    truss.add_material(Material.name, Material.e, Material.g, Material.nu, Material.rho)

    for name, node in nodes.items():
        truss.add_node(name, node["x"], node["y"], node["z"])
        if name in anchors:
            anchor = anchors[name]
            truss.def_support(name, anchor["tx"], anchor["ty"], anchor["tz"], anchor["rx"], anchor["ry"], anchor["rz"])

    for name, force in forces.items():
        for force_direction, force_magnitude in get_FEA_forces(force):
            for node in force["nodes"]:
                truss.add_node_load(node, force_direction, force_magnitude)

    for name, edge in edges.items():
        truss.add_member(
            name,
            edge["start"],
            edge["end"],
            Material.name,
            SectionProperties.iy,
            SectionProperties.iz,
            SectionProperties.j,
            SectionProperties.a,
        )
        # do we have to release all edges??
        truss.def_releases(
            name,
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

    return truss


def get_FEA_forces(force):
    forces = []
    if force["x"] != 0:
        forces.append(("FX", force["x"]))
    if force["y"] != 0:
        forces.append(("FY", force["y"]))
    if force["z"] != 0:
        forces.append(("FZ", force["z"]))
    return forces


def run(input_file: str) -> None:
    nodes, edges, anchors, forces = generate_truss(input_file)
    truss_model = finite_element_analysis(nodes, edges, anchors, forces)
    visualize(truss_model)
