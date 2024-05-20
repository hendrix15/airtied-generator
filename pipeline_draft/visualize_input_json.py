import json
import plotly.graph_objects as go

# Load JSON data
with open('./pipeline_draft/example_input_1.json', 'r') as f:
    data = json.load(f)

anchors = data['anchors']
forces = data['forces']

# Extract coordinates for anchors and forces
coords = {name: (v['x'], v['y'], v['z']) for name, v in anchors.items()}
force_coords = {name: (v['x'], v['y'], v['z']) for name, v in forces.items()}
force_vectors = {name: (v['fx'], v['fy'], v['fz']) for name, v in forces.items()}

# Create scatter plot for anchors and force nodes
scatter_anchors = go.Scatter3d(
    x=[coords[vertex][0] for vertex in coords],
    y=[coords[vertex][1] for vertex in coords],
    z=[coords[vertex][2] for vertex in coords],
    mode='markers+text',
    marker=dict(size=5, color='blue'),
    text=list(coords.keys()),
    textposition="top center"
)

scatter_forces = go.Scatter3d(
    x=[force_coords[vertex][0] for vertex in force_coords],
    y=[force_coords[vertex][1] for vertex in force_coords],
    z=[force_coords[vertex][2] for vertex in force_coords],
    mode='markers+text',
    marker=dict(size=5, color='green'),
    text=list(force_coords.keys()),
    textposition="top center"
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
fig = go.Figure(data=[scatter_anchors, scatter_forces])

# Set labels
fig.update_layout(
    scene=dict(
        xaxis_title='X',
        yaxis_title='Y',
        zaxis_title='Z',
    ),
    title='Tower Visualization with Forces'
)

# Show plot
fig.show()
