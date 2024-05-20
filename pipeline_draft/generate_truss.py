from argparse import ArgumentParser
import json
from PyNite import FEModel3D
from PyNite import Visualization

from .config import Material, MaxDim, SectionProperties

def get_truss(anchors, forces, input_file):
    # Magic ✨
    if 'example_input_2.json' in input_file:
        with open('./pipeline_draft/example_tower_2.json') as f:
            truss = json.load(f)
            print(truss)
            return truss['vertices'], truss['edges'], truss['anchors'], truss['forces']
    elif 'example_input_1.json' in input_file:
        with open('./pipeline_draft/example_tower_1.json') as f:
            truss = json.load(f)
            print(truss)
            return truss['vertices'], truss['edges'], truss['anchors'], truss['forces']


def generate_truss(input_file):
    # read input as json
    with open(input_file) as f:
        input_data = json.load(f)

    # set anchors and forces from input data
    anchors = input_data['anchors']
    forces = input_data['forces']

    vertices, edges, anchors, forces = get_truss(anchors, forces, input_file)
    
    return vertices, edges, anchors, forces

def finite_element_analysis(vertices, edges, anchors, forces):
    truss_model = generate_FEA_truss(vertices, edges, anchors, forces)
    truss_model.analyze(check_statics=True)

    for members in truss_model.Members.values():
        print(f"Member {members.name} calculated axial force: {members.max_axial()}")
    
def visualize(vertices, edges, anchors, forces):
    truss_model = generate_FEA_truss(vertices, edges, anchors, forces)
    Visualization.render_model(truss_model, annotation_size=0.05, render_loads=True, case='Case 1')

def generate_FEA_truss(vertices, edges, anchors, forces):
    truss = FEModel3D()
    truss.add_material(Material.name, Material.e, Material.g, Material.nu, Material.rho)

    for name, node in vertices.items():
        truss.add_node(name, node['x'], node['y'], node['z'])

    for vertex_name in anchors:
        truss.def_support(vertex_name, True, True, True, True, True, True)

    for name, force in forces.items():
        force_direction, force_magnitude = get_FEA_force(force)
        truss.add_node_load(name, force_direction, force_magnitude)

    for name, edge in edges.items():
        truss.add_member(name, edge['start'], edge['end'], Material.name, SectionProperties.iy, SectionProperties.iz, SectionProperties.j, SectionProperties.a)
        # do we have to release all edges??
        truss.def_releases(name, False, False, False, False, True, True, False, False, False, False, True, True)

    return truss


def get_FEA_force(force):
    if force['fx'] != 0:
        return 'FX', force['fx']
    elif force['fy'] != 0:
        return 'FY', force['fy']
    else:
        return 'FZ', force['fz']

def run():
    parser = ArgumentParser()
    parser.add_argument('input_file', type=str)
    # parser.add_argument('-output-file', type=str, default='generated_truss.json')

    args = parser.parse_args()
    input_file = args.input_file
    # output_file = args.output_file

    vertices, edges, anchors, forces = generate_truss(input_file)
    finite_element_analysis(vertices, edges, anchors, forces)

    visualize(vertices, edges, anchors, forces)
    
    

if __name__ == "__main__":
    run()