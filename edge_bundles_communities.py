import math
from collections import defaultdict
from bokeh.palettes import Category10, Category20
from networkx.algorithms.community import greedy_modularity_communities
import networkx as nx
import holoviews as hv
from holoviews import opts
from holoviews.operation.datashader import bundle_graph
from bokeh.models import HoverTool

# from bokeh.models import HoverTool  # only needed if you use the tooltip hook

# Ensure Bokeh backend is initialized in scripts
hv.extension('bokeh')
hv.renderer('bokeh').theme = 'dark_minimal'

# Sizing defaults
defaults = dict(width=800, height=800)
hv.opts.defaults(
    opts.EdgePaths(**defaults),
    opts.Graph(**defaults),
    opts.Nodes(**defaults)
)

# 1) Build a test graph
G = nx.barabasi_albert_graph(n=300, m=4, seed=42)
print("Nodes:", G.number_of_nodes())
print("Edges:", G.number_of_edges())

# 2) Add degree as a node attribute for coloring/hover
deg = dict(G.degree())
nx.set_node_attributes(G, deg, name='degree')

# --- 3) Community detection and grouped circular layout ---
comms = list(greedy_modularity_communities(G))
target_k = 8  # choose any in [5, 10]

comms_sorted = sorted(comms, key=len, reverse=True)
if len(comms_sorted) > target_k:
    kept = comms_sorted[:target_k - 1]
    other = set().union(*comms_sorted[target_k - 1:])
    comms_limited = kept + [other]
elif len(comms_sorted) < 5:
    comms_limited = comms_sorted
else:
    comms_limited = comms_sorted

node2comm = {}
for i, cset in enumerate(comms_limited):
    for n in cset:
        node2comm[n] = i

comm_names = [f"Comm {i+1}" for i in range(len(comms_limited))]
if len(comms_sorted) > target_k:
    comm_names[-1] = "Other"

nx.set_node_attributes(G, node2comm, name='community')

# After comm_names and nx.set_node_attributes(G, node2comm, name='community')
node2comm_label = {n: comm_names[node2comm[n]] for n in node2comm}
nx.set_node_attributes(G, node2comm_label, name='community_label')



def grouped_circular_layout(G, communities, radius=1.0, gap_deg=10.0):
    n_total = G.number_of_nodes()
    k = len(communities)
    gap_total = math.radians(gap_deg) * k
    circle_total = 2 * math.pi
    available = max(circle_total - gap_total, 0.0)

    sizes = [len(c) for c in communities]
    total_size = sum(sizes)
    proportions = [s / total_size if total_size > 0 else 0 for s in sizes]
    arcs = [available * p for p in proportions]

    pos = {}
    theta = 0.0
    gap = math.radians(gap_deg)

    for cset, arc_len in zip(communities, arcs):
        m = len(cset)
        if m == 0:
            theta += arc_len + gap
            continue
        step = arc_len / m if m > 0 else 0
        start = theta + (0.5 * step if m > 1 else 0.0)
        for j, n in enumerate(sorted(cset)):
            t = start + j * step
            pos[n] = (radius * math.cos(t), radius * math.sin(t))
        theta += arc_len + gap
    return pos

pos = grouped_circular_layout(G, comms_limited, radius=1.0, gap_deg=10.0)


# Use Category10/20 as a discrete palette
from bokeh.palettes import Category10, Category20
if len(comms_limited) <= 10:
    palette = Category10[max(3, min(10, len(comms_limited)))]
else:
    palette = Category20[20]

# Include node attributes explicitly so they are available to HoloViews
graph = hv.Graph.from_networkx(
    G, pos, node_attributes=['degree', 'community', 'community_label']
).opts(
    # Nodes (categorical coloring)
    node_size=6,
    node_color='community_label',   # categorical field (strings)
    cmap=palette,
    colorbar=False,                 # no colorbar for categorical
    node_alpha=0.9,
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
    tension=0.8,
    accuracy=150,              # raise to 200–300 for smoother bundles (slower)
    min_segment_length=0.01,
    max_segment_length=0.05
)


def remove_tooltips(plot, element):
    for tool in plot.state.tools:
        if isinstance(tool, HoverTool):
            tool.tooltips = None  # 🔥 this disables the popup
            
bundled = bundled.opts(
    edge_hover_line_color='yellow',
    edge_hover_line_width=3.5,
    tools=['hover'],
    inspection_policy='edges',
    hooks=[remove_tooltips]
)



# 6) Save as standalone interactive HTML
out_file = 'test_edgebundling_3.html'
hv.save(bundled, out_file)
print(f"Saved to {out_file}")

