import networkx as nx
import holoviews as hv
from holoviews import opts
from holoviews.operation.datashader import bundle_graph
from bokeh.models import HoverTool

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
# pos = nx.spring_layout(G, seed=42, dim=2)
pos = nx.circular_layout(G)

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
    edge_hover_line_width=1.5,
    tools=['hover'],
    inspection_policy='edges',
    hooks=[remove_tooltips]
)

from bokeh.themes import Theme
hv.renderer('bokeh').theme = Theme(json={
    'attrs': {
        'Figure': {
            'background_fill_color': '#000000',
            'border_fill_color': '#000000',
            'outline_line_color': '#333333'
        },
        'Grid': {
            'grid_line_color': '#444444'
        },
        'Axis': {
            'major_label_text_color': 'white',
            'axis_label_text_color': 'white',
            'axis_line_color': 'white',
            'major_tick_line_color': 'white',
            'minor_tick_line_color': 'white',
        },
        'Title': {
            'text_color': 'white'
        }
    }
})

#
# # Step 6: Glowing node subset
# glow_nodes = nodes_df[nodes_df['degree'] > 20]
#
# # Step 7: Create glow layers
# def glow_layers(df, n_layers=4, size_start=12, alpha_decay=0.25):
#     layers = []
#     for i in range(n_layers):
#         size = size_start + i * 3
#         alpha = max(0.05, 1 - alpha_decay * i)
#         layer = hv.Nodes(df).opts(
#             size=size,
#             alpha=alpha,
#             color='color',
#             line_color=None,
#             tools=[]
#         )
#         layers.append(layer)
#     return hv.Overlay(layers)
#
# glow = glow_layers(glow_nodes)
#
# main_nodes = hv.Nodes(nodes_df).opts(
#     size=8,
#     color='color',
#     line_color='color',
#     line_width=0.01,
#     tools=['hover'],
#     fill_color='color',
#     hover_fill_color=hovercol,
#     hover_line_color='black',
#     hover_alpha=1.0,
#     nonselection_alpha=0.6,
#     hooks=[remove_tooltips]
# )



# 6) Save as standalone interactive HTML
out_file = 'test_edgebundling_2.html'
hv.save(bundled, out_file)
print(f"Saved to {out_file}")