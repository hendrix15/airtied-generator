import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial import cKDTree

# Define constants
kT = 5e-6  # Scaling factor for tension
kC = 1.5e-5  # Scaling factor for compression
λmax = 1000  # Maximum allowable force in beams


# Generate the grid and return points and beams
def generate_grid():
    # Define anchor and load points for a bridge
    anchors = np.array([[0.0, 0.0, 0.0], [10.0, 0.0, 0.0]])  # Anchor 1  # Anchor 2

    loads = np.array([[2.5, 0.0, 2.0], [7.5, 0.0, 2.0]])  # Load point 1  # Load point 2

    # Create a dense grid of free joints above the loads
    free_points = []
    num_layers = 3  # Number of layers of free joints
    layer_height = 2.0  # Vertical spacing between layers

    for z in np.linspace(2.5, 2.5 + num_layers * layer_height, num_layers):
        for x in np.linspace(0, 10, 6):
            free_points.append([x, 0, z])
    free_points = np.array(free_points)

    # Combine all points
    points = np.vstack((anchors, loads, free_points))

    # Define initial beam connections by finding nearest neighbors
    beams = find_nearest_neighbors(points, k=3)

    return points, beams


# Find nearest neighbors for beam connections
def find_nearest_neighbors(points, k=3):
    tree = cKDTree(points)
    neighbors = []
    for i in range(len(points)):
        distances, indices = tree.query(points[i], k=k + 1)
        for j in indices:
            if i != j:
                neighbors.append((i, j))
    # Remove duplicate connections
    return list(set(tuple(sorted(beam)) for beam in neighbors))


# Define the objective function to minimize the mass
def objective_function(x, points, beams):
    total_mass = 0.0
    for i, beam in enumerate(beams):
        point_a = points[beam[0]]
        point_b = points[beam[1]]
        length = np.linalg.norm(point_a - point_b)
        force = x[i]
        # Check if force is tension or compression
        if force < 0:  # Tension
            mass = -kT * force * length
        else:  # Compression
            mass = kC * np.sqrt(force) * length
        total_mass += mass
    return total_mass


# Define the force balance constraints at each joint
def force_balance_constraints(x, points, beams, anchors):
    constraints = []
    for i in range(len(points)):
        if i < len(anchors):  # Ignore anchors in force balance constraints
            continue
        # Calculate net force at joint i
        net_force = np.zeros(3)
        for j, beam in enumerate(beams):
            if i in beam:
                other_point = beam[1] if beam[0] == i else beam[0]
                direction = points[other_point] - points[i]
                direction /= np.linalg.norm(direction)
                net_force += direction * x[j]
        constraints.extend(net_force)
    return np.array(constraints)


# Wrapper function for constraints
def combined_constraints(x, points, beams, anchors):
    return force_balance_constraints(x, points, beams, anchors)


# Optimize the structure
def optimize_structure(points, beams, anchors):
    initial_guess = np.ones(len(beams))
    bounds = [(-λmax, λmax)] * len(beams)

    constraints = [
        {"type": "eq", "fun": lambda x: combined_constraints(x, points, beams, anchors)}
    ]

    print("Starting optimization...")
    try:
        result = minimize(
            objective_function,
            initial_guess,
            args=(points, beams),
            bounds=bounds,
            constraints=constraints,
        )
        if not result.success:
            print("Optimization failed:", result.message)
        return result
    except Exception as e:
        print("Optimization error:", e)
        return None


# Visualization function with load points colored in yellow
def plot_truss(points, beams, title="Bridge Truss Structure"):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    # Plot anchors in blue
    ax.scatter(
        points[:2, 0],
        points[:2, 1],
        points[:2, 2],
        c="blue",
        marker="o",
        label="Anchors",
    )

    # Plot load points in yellow
    ax.scatter(
        points[2:4, 0],
        points[2:4, 1],
        points[2:4, 2],
        c="yellow",
        marker="o",
        label="Loads",
    )

    # Plot free joints in red
    ax.scatter(
        points[4:, 0],
        points[4:, 1],
        points[4:, 2],
        c="red",
        marker="o",
        label="Free Joints",
    )

    for beam in beams:
        point_a = points[beam[0]]
        point_b = points[beam[1]]
        ax.plot(
            [point_a[0], point_b[0]],
            [point_a[1], point_b[1]],
            [point_a[2], point_b[2]],
            "b-",
        )

    ax.set_title(title)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    plt.legend()
    plt.show()


# Main function
def main():
    # Generate grid and beams
    points, beams = generate_grid()
    anchors = points[:2]

    # Plot the initial dense grid
    plot_truss(
        points, beams, title="Initial Nearest Neighbor Grid for Bridge Truss Structure"
    )

    # Optimize the structure
    result = optimize_structure(points, beams, anchors)

    if result:
        # Print results
        print("Optimal Forces in Beams:", result.x)
        print("Optimal Mass:", result.fun)

        # Update positions of free joints (example of handling geometry optimization)
        free_points_optimal = points[
            4:
        ]  # Keeping free points positions fixed for visualization
        points[4:] = free_points_optimal

        # Plot the optimized structure
        plot_truss(points, beams, title="Optimized Bridge Truss Structure")


# Entry point
if __name__ == "__main__":
    main()
