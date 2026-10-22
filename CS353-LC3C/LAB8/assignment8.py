"""
CS353 - Computer Networks Lab
Week 8 / Lab 8: Computing the Sink Tree with Dijkstra's Algorithm

Name    : SAYAN SHIT
Roll No : 2401179
"""

import sys

class NetworkGraph:
    def __init__(self):
        # Adjacency list: node -> list of (neighbor, cost)
        self.adj = {}
        self.nodes = set()

    def add_edge(self, u: str, v: str, cost: int):
        """Adds an undirected edge between u and v with the given cost."""
        self.nodes.add(u)
        self.nodes.add(v)
        
        if u not in self.adj:
            self.adj[u] = []
        if v not in self.adj:
            self.adj[v] = []
            
        self.adj[u].append((v, cost))
        self.adj[v].append((u, cost))

    def get_neighbors(self, u: str):
        """Returns sorted list of (neighbor, cost) for node u."""
        return sorted(self.adj.get(u, []), key=lambda x: x[0])

    def print_topology(self):
        """Prints each router's neighbors with costs (Part A)."""
        print("=" * 65)
        print("PART A: NETWORK TOPOLOGY (ADJACENCY STRUCTURE)")
        print("=" * 65)
        for node in sorted(self.nodes):
            neighbors_str = ", ".join(f"{nbr} (cost: {cost})" for nbr, cost in self.get_neighbors(node))
            print(f"Router {node} -> {neighbors_str}")
        print()

    def compute_sink_tree(self, sink: str):
        """
        Runs Dijkstra's algorithm from the sink node to find the least-cost path
        and next-hop (parent in the sink tree) for all routers.
        
        Tie-break rule:
        When a node can reach the sink by two paths of equal cost, choose the
        one whose next hop (candidate parent) has the smaller label.
        """
        if sink not in self.nodes:
            raise ValueError(f"Sink node {sink} not found in graph.")

        sorted_nodes = sorted(self.nodes)
        dist = {node: float('inf') for node in sorted_nodes}
        pred = {node: None for node in sorted_nodes}
        
        dist[sink] = 0
        finalized = set()

        while len(finalized) < len(sorted_nodes):
            # Select unfinalized node with minimum tentative distance.
            # Tie-break among nodes with identical minimum distance by node label.
            unfinalized = [n for n in sorted_nodes if n not in finalized]
            u = min(unfinalized, key=lambda n: (dist[n], n))
            
            finalized.add(u)

            # Relax all incident links
            for v, cost in self.get_neighbors(u):
                if v not in finalized:
                    tentative = dist[u] + cost
                    if tentative < dist[v]:
                        dist[v] = tentative
                        pred[v] = u
                    elif tentative == dist[v]:
                        # Tie-break rule: smaller label next-hop wins
                        if pred[v] is None or u < pred[v]:
                            pred[v] = u

        return dist, pred

    def get_sink_tree_edges(self, sink: str, pred: dict):
        """
        Returns the edges of the sink tree as (node, parent) pairs
        for every router except the sink, sorted alphabetically by node.
        """
        edges = []
        for node in sorted(self.nodes):
            if node != sink and pred[node] is not None:
                edges.append((node, pred[node]))
        return edges

    def build_forwarding_table(self, sink: str, dist: dict, pred: dict):
        """
        Builds the forwarding table for each router to reach the sink.
        For each router, records the next hop and total path cost.
        """
        table = []
        for node in sorted(self.nodes):
            if node == sink:
                table.append((node, "(local)", dist[node]))
            else:
                table.append((node, pred[node], dist[node]))
        return table

    def verify_spanning_tree(self, sink: str, pred: dict):
        """
        Part D: Verifies that the computed sink tree is a valid spanning tree:
        1. Has exactly N - 1 edges.
        2. Reaches every router (every router can reach the sink).
        3. Contains no cycles.
        """
        n = len(self.nodes)
        tree_edges = self.get_sink_tree_edges(sink, pred)
        edge_count = len(tree_edges)

        # Condition 1: Exactly N - 1 edges
        has_n_minus_1_edges = (edge_count == n - 1)

        # Condition 2 & 3: Reachability to sink and acyclicity
        reaches_sink_all = True
        cycle_detected = False

        for node in self.nodes:
            if node == sink:
                continue
            curr = node
            visited = set()
            while curr != sink and curr is not None:
                if curr in visited:
                    cycle_detected = True
                    break
                visited.add(curr)
                curr = pred[curr]
            
            if curr != sink:
                reaches_sink_all = False

        is_valid = has_n_minus_1_edges and reaches_sink_all and (not cycle_detected)

        return {
            "is_valid": is_valid,
            "total_nodes": n,
            "edge_count": edge_count,
            "has_n_minus_1_edges": has_n_minus_1_edges,
            "reaches_all_routers": reaches_sink_all,
            "has_no_cycles": not cycle_detected,
        }


def format_costs(dist: dict, sink: str):
    """Formats costs in the test vector format: A = 8, B = 6, ..."""
    items = [f"{k} = {dist[k]}" for k in sorted(dist.keys())]
    return f"Cost to {sink}: " + ", ".join(items)


def format_next_hops(pred: dict, sink: str):
    """Formats next hops in the test vector format: A to B, B to D, ..."""
    items = [f"{node} to {parent}" for node, parent in sorted(pred.items()) if node != sink and parent is not None]
    return f"Next hop toward {sink}: " + ", ".join(items)


def format_edges(edges: list):
    """Formats tree edges in the test vector format: (A, B), (B, D), ..."""
    items = [f"({u}, {v})" for u, v in edges]
    return "Sink-tree edges (node, parent): " + ", ".join(items)


def print_forwarding_table(sink: str, table: list):
    """Prints a clean ASCII forwarding table."""
    print(f"\nForwarding Table for Destination (Sink) = {sink}:")
    print("+--------+----------+-------+")
    print("| Router | Next Hop |  Cost |")
    print("+--------+----------+-------+")
    for router, next_hop, cost in table:
        print(f"|   {router:<4} |   {next_hop:<6} |  {cost:<4} |")
    print("+--------+----------+-------+")


def run_pipeline():
    # -------------------------------------------------------------
    # Base Topology Definition
    # -------------------------------------------------------------
    base_edges = [
        ("A", "B", 2),
        ("A", "C", 5),
        ("B", "C", 1),
        ("B", "D", 4),
        ("C", "E", 3),
        ("D", "E", 1),
        ("D", "F", 2),
        ("E", "F", 6),
    ]

    graph = NetworkGraph()
    for u, v, w in base_edges:
        graph.add_edge(u, v, w)

    # Part A: Represent Topology
    graph.print_topology()

    # -------------------------------------------------------------
    # Vector 1: Sink = F
    # -------------------------------------------------------------
    print("=" * 65)
    print("TEST VECTOR 1: SINK = F (BASE TOPOLOGY)")
    print("=" * 65)
    dist_v1, pred_v1 = graph.compute_sink_tree("F")
    edges_v1 = graph.get_sink_tree_edges("F", pred_v1)
    table_v1 = graph.build_forwarding_table("F", dist_v1, pred_v1)

    print(format_costs(dist_v1, "F"))
    print(format_next_hops(pred_v1, "F"))
    print(format_edges(edges_v1))
    print_forwarding_table("F", table_v1)

    # Verification against expected Vector 1
    expected_costs_v1 = {"A": 8, "B": 6, "C": 6, "D": 2, "E": 3, "F": 0}
    expected_hops_v1 = {"A": "B", "B": "D", "C": "E", "D": "F", "E": "D"}
    expected_edges_v1 = [("A", "B"), ("B", "D"), ("C", "E"), ("D", "F"), ("E", "D")]
    assert dist_v1 == expected_costs_v1, "Vector 1 costs mismatch!"
    assert {k: pred_v1[k] for k in expected_hops_v1} == expected_hops_v1, "Vector 1 next-hops mismatch!"
    assert edges_v1 == expected_edges_v1, "Vector 1 tree edges mismatch!"
    print(">>> Vector 1 Result: PASS (Matches specification exactly)\n")

    # -------------------------------------------------------------
    # Vector 2: Sink = A
    # -------------------------------------------------------------
    print("=" * 65)
    print("TEST VECTOR 2: SINK = A (BASE TOPOLOGY)")
    print("=" * 65)
    dist_v2, pred_v2 = graph.compute_sink_tree("A")
    edges_v2 = graph.get_sink_tree_edges("A", pred_v2)
    table_v2 = graph.build_forwarding_table("A", dist_v2, pred_v2)

    print(format_costs(dist_v2, "A"))
    print(format_next_hops(pred_v2, "A"))
    print(format_edges(edges_v2))
    print_forwarding_table("A", table_v2)

    # Verification against expected Vector 2
    expected_costs_v2 = {"A": 0, "B": 2, "C": 3, "D": 6, "E": 6, "F": 8}
    expected_hops_v2 = {"B": "A", "C": "B", "D": "B", "E": "C", "F": "D"}
    expected_edges_v2 = [("B", "A"), ("C", "B"), ("D", "B"), ("E", "C"), ("F", "D")]
    assert dist_v2 == expected_costs_v2, "Vector 2 costs mismatch!"
    assert {k: pred_v2[k] for k in expected_hops_v2} == expected_hops_v2, "Vector 2 next-hops mismatch!"
    assert edges_v2 == expected_edges_v2, "Vector 2 tree edges mismatch!"
    print(">>> Vector 2 Result: PASS (Matches specification exactly)\n")

    # -------------------------------------------------------------
    # Part D: Properties Verification & Rerouting Experiment
    # -------------------------------------------------------------
    print("=" * 65)
    print("PART D: PROPERTIES AND REROUTING EXPERIMENT")
    print("=" * 65)

    # Task 1: Spanning Tree Property Checks
    print("--- Task 1: Spanning Tree Property Verification (Sink = F) ---")
    tree_check_v1 = graph.verify_spanning_tree("F", pred_v1)
    print(f"Total Routers (N)               : {tree_check_v1['total_nodes']}")
    print(f"Sink-Tree Edge Count            : {tree_check_v1['edge_count']}")
    print(f"Has exactly N - 1 edges?        : {tree_check_v1['has_n_minus_1_edges']} (5 == 6 - 1)")
    print(f"Reaches every router to sink?   : {tree_check_v1['reaches_all_routers']}")
    print(f"Contains no cycles (acyclic)?   : {tree_check_v1['has_no_cycles']}")
    print(f"Is a valid Spanning Tree?       : {tree_check_v1['is_valid']}\n")

    # Task 2: Modified Topology (Raise link D-F cost from 2 to 9)
    print("--- Task 2: Modified Topology Rerouting Experiment (Vector 3) ---")
    mod_edges = [
        ("A", "B", 2),
        ("A", "C", 5),
        ("B", "C", 1),
        ("B", "D", 4),
        ("C", "E", 3),
        ("D", "E", 1),
        ("D", "F", 9),  # Link cost raised from 2 to 9
        ("E", "F", 6),
    ]

    mod_graph = NetworkGraph()
    for u, v, w in mod_edges:
        mod_graph.add_edge(u, v, w)

    dist_v3, pred_v3 = mod_graph.compute_sink_tree("F")
    edges_v3 = mod_graph.get_sink_tree_edges("F", pred_v3)
    table_v3 = mod_graph.build_forwarding_table("F", dist_v3, pred_v3)

    print("Modified Topology: Link D-F cost raised from 2 to 9.")
    print(format_costs(dist_v3, "F"))
    print(format_next_hops(pred_v3, "F"))
    print(format_edges(edges_v3))
    print_forwarding_table("F", table_v3)

    # Verification against expected Vector 3
    expected_costs_v3 = {"A": 12, "B": 10, "C": 9, "D": 7, "E": 6, "F": 0}
    expected_hops_v3 = {"A": "B", "B": "C", "C": "E", "D": "E", "E": "F"}
    expected_edges_v3 = [("A", "B"), ("B", "C"), ("C", "E"), ("D", "E"), ("E", "F")]
    assert dist_v3 == expected_costs_v3, "Vector 3 costs mismatch!"
    assert {k: pred_v3[k] for k in expected_hops_v3} == expected_hops_v3, "Vector 3 next-hops mismatch!"
    assert edges_v3 == expected_edges_v3, "Vector 3 tree edges mismatch!"
    print(">>> Vector 3 Result: PASS (Matches specification exactly)\n")

    # Tree changes analysis
    set_v1 = set(edges_v1)
    set_v3 = set(edges_v3)
    removed_edges = sorted(list(set_v1 - set_v3))
    added_edges = sorted(list(set_v3 - set_v1))
    unchanged_edges = sorted(list(set_v1 & set_v3))

    print("Sink Tree Edge Changes (Vector 1 -> Vector 3):")
    print(f"  Removed Edges   : {', '.join(f'({u}, {v})' for u, v in removed_edges)}")
    print(f"  Added Edges     : {', '.join(f'({u}, {v})' for u, v in added_edges)}")
    print(f"  Unchanged Edges : {', '.join(f'({u}, {v})' for u, v in unchanged_edges)}")
    print()

    # Spanning tree check for Vector 3
    tree_check_v3 = mod_graph.verify_spanning_tree("F", pred_v3)
    print(f"Vector 3 Spanning Tree Check Valid? : {tree_check_v3['is_valid']}\n")

    # Written Explanations for Part D.2 and Part D.3
    print("--- Task 2 & Task 3: Written Explanations ---")
    print("Explanation for Part D.2 (Optimality Principle & Rerouting):")
    d2_explanation = (
        "Under the original topology, the least-cost path from D to F was direct (D-F, cost 2), "
        "and router E reached F via D (E->D->F, cost 1+2=3 < 6). When the cost of link D-F increases "
        "from 2 to 9, the direct link E-F (cost 6) becomes cheaper than going through D (1+9=10). "
        "Router D now finds a cheaper route to F through E (D->E->F, cost 1+6=7) rather than its direct "
        "link of cost 9. By the Optimality Principle, if router E lies on the optimal path from D (or C, B, A) "
        "to F, then the remaining portion of that path must be the optimal path from E to F (which is now E->F). "
        "Consequently, traffic that previously converged on D to reach F now pivots to route through E, "
        "replacing tree edges (B, D), (D, F), and (E, D) with (B, C), (D, E), and (E, F)."
    )
    print(d2_explanation)
    print()

    print("Explanation for Part D.3 (Undirected Equivalence & Asymmetric Counterexample):")
    d3_explanation = (
        "On an undirected graph, all link costs are symmetric, meaning cost(u, v) = cost(v, u). "
        "Because path costs are symmetric sums, the least-cost path from any node X to destination D "
        "is simply the exact reverse of the least-cost path from D to X; thus, Dijkstra run once from D "
        "discovers the reverse shortest paths from all sources, making Dijkstra's predecessors identical to "
        "each node's next hop toward D. The two would differ in directed networks with asymmetric link costs "
        "(such as asymmetric bandwidth/propagation or policy routing where cost(u->v) != cost(v->u)), where "
        "the forward shortest path from D to X does not correspond to the reverse path from X to D."
    )
    print(d3_explanation)
    print("=" * 65)


if __name__ == "__main__":
    run_pipeline()
