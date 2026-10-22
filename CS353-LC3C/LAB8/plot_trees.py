"""
Generates topology_and_sink_trees.png for Lab 8
Visualizes:
1. Base Network Topology
2. Sink Tree for Destination F (Vector 1)
3. Sink Tree for Destination A (Vector 2)
4. Rerouted Sink Tree for Destination F with D-F=9 (Vector 3)
"""

import matplotlib.pyplot as plt
import numpy as np

# Fixed 2D planar coordinates for clean, non-overlapping visualization
pos = {
    'A': (0.2, 2.2),
    'B': (2.2, 2.2),
    'D': (4.2, 2.2),
    'C': (1.2, 0.4),
    'E': (3.2, 0.4),
    'F': (5.2, 0.4)
}

fig, axes = plt.subplots(1, 4, figsize=(24, 6.5))

def draw_network(ax, title, edges, tree_edges=None, sink=None, changed_info=None):
    ax.set_title(title, fontsize=13, fontweight='bold', pad=15)
    ax.set_xlim(-0.6, 6.0)
    ax.set_ylim(-0.4, 2.9)
    ax.axis('off')

    # 1. Draw all underlying graph links in light gray with cost badges
    for u, v, w in edges:
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        ax.plot([x1, x2], [y1, y2], color='#cbd5e1', lw=2.5, zorder=1)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx, my, f'{w}', fontsize=11, fontweight='bold', color='#334155',
                ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.25', facecolor='#f8fafc', edgecolor='#94a3b8', lw=1.2),
                zorder=2)

    # 2. Draw directed sink-tree edges (pointing from node to parent/next-hop toward sink)
    if tree_edges:
        for u, parent in tree_edges:
            x1, y1 = pos[u]
            x2, y2 = pos[parent]
            color = '#2563eb'  # default tree color (blue)
            lw = 3.5
            if changed_info and (u, parent) in changed_info.get('added', []):
                color = '#16a34a'  # green for newly added routes in Vector 3
            
            dx, dy = x2 - x1, y2 - y1
            dist = np.hypot(dx, dy)
            r = 0.35  # radius offset so arrow head doesn't hide behind node
            sx, sy = x1 + dx * (r / dist), y1 + dy * (r / dist)
            ex, ey = x2 - dx * (r / dist), y2 - dy * (r / dist)
            
            ax.annotate('', xy=(ex, ey), xytext=(sx, sy),
                        arrowprops=dict(arrowstyle='->,head_width=0.45,head_length=0.7',
                                        color=color, lw=lw),
                        zorder=4)

    # 3. Highlight broken/removed edges from original tree (red dashed)
    if changed_info and 'removed' in changed_info:
        for u, parent in changed_info['removed']:
            x1, y1 = pos[u]
            x2, y2 = pos[parent]
            ax.plot([x1, x2], [y1, y2], color='#dc2626', lw=2.2, ls='--', zorder=3)

    # 4. Draw router nodes
    for node, (x, y) in pos.items():
        if node == sink:
            fc = '#ef4444'  # Red for destination sink
            ec = '#991b1b'
            label_text = f'{node}\n(Sink)'
        else:
            fc = '#3b82f6'  # Blue for routers
            ec = '#1d4ed8'
            label_text = node
        
        ax.scatter([x], [y], s=1200, color=fc, edgecolors=ec, linewidth=2.5, zorder=5)
        ax.text(x, y, label_text, color='white', fontsize=11, fontweight='bold',
                ha='center', va='center', zorder=6)

# Base topology edges
base_edges = [
    ('A', 'B', 2), ('A', 'C', 5), ('B', 'C', 1), ('B', 'D', 4),
    ('C', 'E', 3), ('D', 'E', 1), ('D', 'F', 2), ('E', 'F', 6)
]

# Modified topology edges (D-F raised from 2 to 9)
mod_edges = [
    ('A', 'B', 2), ('A', 'C', 5), ('B', 'C', 1), ('B', 'D', 4),
    ('C', 'E', 3), ('D', 'E', 1), ('D', 'F', 9), ('E', 'F', 6)
]

# Panel 1: Original Topology
draw_network(axes[0], '1. Base Network Topology\n(Undirected, positive link costs)', base_edges)

# Panel 2: Vector 1 (Sink F)
edges_v1 = [('A', 'B'), ('B', 'D'), ('C', 'E'), ('D', 'F'), ('E', 'D')]
draw_network(axes[1], '2. Vector 1: Sink Tree (Sink = F)\nLeast-cost paths converge via D', base_edges, tree_edges=edges_v1, sink='F')

# Panel 3: Vector 2 (Sink A)
edges_v2 = [('B', 'A'), ('C', 'B'), ('D', 'B'), ('E', 'C'), ('F', 'D')]
draw_network(axes[2], '3. Vector 2: Sink Tree (Sink = A)\nLeast-cost paths converge to A', base_edges, tree_edges=edges_v2, sink='A')

# Panel 4: Vector 3 (Modified DF=9, Sink F)
edges_v3 = [('A', 'B'), ('B', 'C'), ('C', 'E'), ('D', 'E'), ('E', 'F')]
changed = {
    'removed': [('B', 'D'), ('D', 'F'), ('E', 'D')],
    'added': [('B', 'C'), ('D', 'E'), ('E', 'F')]
}
draw_network(axes[3], '4. Vector 3: Rerouted Tree (Sink = F, D-F=9)\nGreen: New routes | Red dashed: Broken', mod_edges, tree_edges=edges_v3, sink='F', changed_info=changed)

plt.tight_layout()
plt.savefig('topology_and_sink_trees.png', dpi=300)
print("Saved 'topology_and_sink_trees.png' successfully.")
