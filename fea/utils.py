import math

from search.models import Edge

# 110g per m for d=0,2m beam = 1.08N
# 275g per m for d=0,5m beam = 2.7N


class Material:
    """Material used for Finite Element Analysis"""

    name = "Airtied"
    e = 199.95  # Modulus of elasticity (GPa)
    g = 78.60  # Shear modulus (GPa)
    nu = 0.30  # Poisson's ratio
    rho = 1 / (math.pi * math.pow((0.2 / 2), 2) * 1) * 0.11  # Density (kg per m^3)


class SectionProperties:
    """Section Properties used for Finite Element Analysis"""

    iy = 0.0000072  # Weak axis moment of inertia (m^4)
    iz = 0.000085  # Strong axis moment of inertia (m^4)
    j = 1.249e-7  # Torsional constant (m^4)
    a = math.pi * math.pow((0.2 / 2), 2)  # Cross-sectional area (m^2)


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
