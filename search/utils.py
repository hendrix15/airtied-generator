import json
import os

import plotly.graph_objects as go
import yaml
from PyNite import FEModel3D

from search.config import Material, SectionProperties
from search.models import Bool3, Edge, Node, Vector3


def read_json(filename: str) -> tuple[list[Node], list[Edge]]:
    nodes = []
    edges = []
    with open(filename) as f:
        data = json.load(f)
        for id, coordinates in data["nodes"].items():
            if id in data["anchors"]:
                anchor = data["anchors"][id]
                nodes.append(
                    Node(
                        id=id,
                        vec=Vector3(
                            x=coordinates["x"], y=coordinates["y"], z=coordinates["z"]
                        ),
                        r_support=Bool3(x=anchor["rx"], y=anchor["ry"], z=anchor["rz"]),
                        t_support=Bool3(x=anchor["tx"], y=anchor["ty"], z=anchor["tz"]),
                        fixed=True,
                    )
                )
            else:
                nodes.append(
                    Node(
                        id=id,
                        vec=Vector3(
                            x=coordinates["x"], y=coordinates["y"], z=coordinates["z"]
                        ),
                        fixed=True,
                    )
                )
        for id, force in data["forces"].items():
            for node_id in force["nodes"]:
                node = next(node for node in nodes if node.id == node_id)
                node.load = Vector3(x=force["x"], y=force["y"], z=force["z"])
        if "edges" in data:
            for id, values in data["edges"].items():
                u = next(node for node in nodes if node.id == values["start"])
                v = next(node for node in nodes if node.id == values["end"])
                edges.append(Edge(id, u, v))
    return nodes, edges


def write_json(
    dirname: str, filename: str, nodes: list[Node], edges: list[Edge]
) -> None:
    os.makedirs(dirname, exist_ok=True)
    result = {"nodes": {}, "edges": {}, "anchors": {}, "forces": {}}
    for node in nodes:
        result["nodes"][node.id] = {"x": node.vec.x, "y": node.vec.y, "z": node.vec.z}
        if node.r_support and node.t_support:
            result["anchors"][node.id] = {
                "rx": node.r_support.x,
                "ry": node.r_support.y,
                "rz": node.r_support.z,
                "tx": node.t_support.x,
                "ty": node.t_support.y,
                "tz": node.t_support.z,
            }
    for edge in edges:
        result["edges"][edge.id] = {"start": edge.u.id, "end": edge.v.id}
    with open(f"{dirname}{filename}", "w") as f:
        json.dump(result, f)


def load_config(filename: str) -> dict:
    with open(filename) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config


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

    return truss


def visualize(
    dirname: str, filename: str, nodes: list[Node], edges: list[Edge]
) -> None:
    os.makedirs(dirname, exist_ok=True)
    input_anchors = {
        node.id: (node.vec.x, node.vec.y, node.vec.z)
        for node in nodes
        if node.fixed and node.r_support and node.t_support
    }
    input_nodes = {
        node.id: (node.vec.x, node.vec.y, node.vec.z)
        for node in nodes
        if node.fixed and not node.r_support and not node.t_support
    }
    other_nodes = {
        node.id: (node.vec.x, node.vec.y, node.vec.z)
        for node in nodes
        if not node.fixed
    }

    generated_edges = []
    for edge in edges:
        generated_edges.append((edge.u.vec.x, edge.u.vec.y, edge.u.vec.z))
        generated_edges.append((edge.v.vec.x, edge.v.vec.y, edge.v.vec.z))

    # force_coords = {name: (v["x"], v["y"], v["z"]) for name, v in forces.items()}
    # force_vectors = {name: (v["fx"], v["fy"], v["fz"]) for name, v in forces.items()}

    scatter_input_anchors = go.Scatter3d(
        x=[input_anchors[name][0] for name in input_anchors],
        y=[input_anchors[name][1] for name in input_anchors],
        z=[input_anchors[name][2] for name in input_anchors],
        mode="markers+text",
        marker=dict(size=5, color="blue"),
        text=list(input_anchors.keys()),
        textposition="top center",
    )

    scatter_input_nodes = go.Scatter3d(
        x=[input_nodes[name][0] for name in input_nodes],
        y=[input_nodes[name][1] for name in input_nodes],
        z=[input_nodes[name][2] for name in input_nodes],
        mode="markers+text",
        marker=dict(size=5, color="green"),
        text=list(input_nodes.keys()),
        textposition="top center",
    )

    scatter_other_nodes = go.Scatter3d(
        x=[other_nodes[name][0] for name in other_nodes],
        y=[other_nodes[name][1] for name in other_nodes],
        z=[other_nodes[name][2] for name in other_nodes],
        mode="markers+text",
        marker=dict(size=5, color="red"),
        text=list(other_nodes.keys()),
        textposition="top center",
    )

    scatter_generated_edges = go.Scatter3d(
        x=[generated_edge[0] for generated_edge in generated_edges],
        y=[generated_edge[1] for generated_edge in generated_edges],
        z=[generated_edge[2] for generated_edge in generated_edges],
        mode="lines",
        name="lines",
    )

    # Create arrows for force vectors
    # force_arrows = []
    # for name, (fx, fy, fz) in force_vectors.items():
    #     x, y, z = force_coords[name]
    #     force_arrows.append(go.Cone(
    #         x=[x],
    #         y=[y],
    #         z=[z],
    #         u=[fx],
    #         v=[fy],
    #         w=[fz],
    #         sizemode="scaled",
    #         sizeref=2,
    #         anchor="tip",
    #         colorscale=[[0, 'red'], [1, 'red']],
    #         showscale=False
    #     ))

    # Combine all elements
    # fig = go.Figure(data=[scatter_anchors, scatter_forces] + force_arrows)
    fig = go.Figure(
        data=[
            scatter_input_anchors,
            scatter_input_nodes,
            scatter_other_nodes,
            scatter_generated_edges,
        ]
    )

    # Set labels
    fig.update_layout(
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z",
        ),
        title="Tower Visualization with Forces",
    )

    # Show plot
    fig.write_image(f"{dirname}{filename}")
