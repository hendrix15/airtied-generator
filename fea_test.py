from utils.fea import fea_opensees, fea_pynite
from utils.parser import read_json


def main() -> None:
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
    main()
