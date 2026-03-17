import networkx as nx
import holoviews as hv
from holoviews import opts
from holoviews.operation.datashader import bundle_graph

# hv.extension('bokeh')
hv.renderer('bokeh').theme = 'dark_minimal'


# Sizing defaults
defaults = dict(width=800, height=800)
hv.opts.defaults(
    opts.EdgePaths(**defaults),
    opts.Graph(**defaults),
    opts.Nodes(**defaults)
)

# 1) Build a test graph (you can increase n later)
G = nx.barabasi_albert_graph(n=600, m=4, seed=42)
print("Nodes:", G.number_of_nodes())
print("Edges:", G.number_of_edges())

# 2) Add degree as a node attribute for coloring
deg = dict(G.degree())
nx.set_node_attributes(G, deg, name='degree')

# 3) Layout (spring is a good default; deterministic with seed)
pos = nx.spring_layout(G, seed=42, dim=2)

# 4) Create HoloViews Graph
# graph = hv.Graph.from_networkx(G, pos).opts(
#     cmap="Blues",
#     node_size=6,
#     edge_line_width=0.25,
#     node_line_color='dimgray',
#     node_color='degree',
#     edge_color='dimgrey'
# )

graph = hv.Graph.from_networkx(G, pos).opts(
    # Nodes
    node_size=6,
    node_color='#fb8100',
    cmap='Viridis',
    clim=(min(dict(G.degree()).values()), max(dict(G.degree()).values())),
    colorbar=True,
    node_alpha=0.8,
    node_line_color='white',
    node_line_width=0.3,

    # Edges
    edge_color='white',
    edge_alpha=0.15,
    edge_line_width=0.7,

    # Plot
    bgcolor='black',
    xaxis=None, yaxis=None,
    show_frame=False,
    tools=['pan', 'wheel_zoom', 'reset', 'hover'],
    active_tools=['wheel_zoom']
)



# 5) Bundle edges (tune parameters for quality vs speed)
bundled = bundle_graph(
    graph,
    tension=0.2,
    accuracy=150,              # raise to 200–300 for smoother bundles (slower)
    min_segment_length=0.01,
    max_segment_length=0.05
)

# 6) Save as standalone interactive HTML
out_file = 'test_edgebundling.html'
hv.save(bundled, out_file)
print(f"Saved to {out_file}")