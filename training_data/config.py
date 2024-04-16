class MaxDim:
    """Default maximum dimensions of generated training data"""

    x = 100
    y = 100
    z = 200


class Material:
    """Material used for Finite Element Analysis"""

    name = "Steel"
    e = 29000  # (ksi) Modulus of elasticity
    g = 11400  # (ksi) Shear modulus
    nu = 0.30  # Poisson's ratio
    rho = 0.000283  # (kci) Density


class SectionProperties:
    """Section Properties used for Finite Element Analysis"""

    iy = 17.3  # (in**4) Weak axis moment of inertia
    iz = 204  # (in**4) Strong axis moment of inertia
    j = 0.300  # (in**4) Torsional constant
    a = 7.65  # (in**2) Cross-sectional area
