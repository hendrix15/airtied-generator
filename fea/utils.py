import math

from utils.config import load_config
from utils.models import Edge


class Material:
    def __init__(self) -> None:
        config = load_config("fea/coefficients.yaml")
        args = config.get("material", {})
        self.e = args["e"]
        self.g = args["g"]
        self.nu = args["nu"]
        self.rho = args["rho"]


class SectionProperties:
    def __init__(self) -> None:
        config = load_config("fea/coefficients.yaml")
        args = config.get("section_properties", {})
        self.iy = args["iy"]
        self.iz = args["iz"]
        self.j = args["j"]
        self.a = args["a"]


class ForceType:
    TENSION = "TENSION"
    COMPRESSION = "COMPRESSION"


def get_euler_load(l: float, force_type: ForceType) -> float:
    if force_type == ForceType.COMPRESSION:
        # gravitational acceleration and load-bearing capacity for a beam with 1m length in kg
        return 35 / math.pow(l, 2)
    return 700


def get_breaking_compression_tension_edges(
    edges: list[Edge], max_forces: dict
) -> list[dict]:
    edges = get_all_compression_tension_edges(edges, max_forces)
    force_edges = []
    for edge in edges:
        if abs(edge["max_force"]) > edge["euler_load"]:
            force_edges.append(edge)
    return force_edges


def get_all_compression_tension_edges(
    edges: list[Edge], max_forces: dict
) -> list[dict]:
    force_edges = []
    for edge in edges:
        max_force = max_forces[edge.id]
        force_type = ForceType.COMPRESSION if max_force > 0 else ForceType.TENSION
        euler_load = get_euler_load(l=edge.length(), force_type=force_type)
        force_edges.append(
            {
                "id": edge.id,
                "force_type": force_type,
                "max_force": max_force,
                "euler_load": euler_load,
            }
        )
    return force_edges
