class MaxDim:
    """Default maximum dimensions of generated training data"""

    x = 100
    y = 100
    z = 200


class Material:
    """Material used for Finite Element Analysis"""

    name = "Steel"
    e = 1  # (ksi) Modulus of elasticity
    g = 1  # (ksi) Shear modulus
    nu = 1  # Poisson's ratio
    rho = 1  # (kci) Density


class SectionProperties:
    """Section Properties used for Finite Element Analysis"""

    iy = 1  # (in**4) Weak axis moment of inertia # euler buckling -> look up table
    iz = 1  # (in**4) Strong axis moment of inertia # 
    j = 1  # (in**4) Torsional constant
    a = 1 # (in**2) Cross-sectional area
