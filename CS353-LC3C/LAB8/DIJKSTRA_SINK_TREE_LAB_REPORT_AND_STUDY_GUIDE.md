# CS353: Computing the Sink Tree with Dijkstra's Algorithm
## Comprehensive Lab Report, Theory Guide & Implementation Manual
**Course:** CS353 · Computer Networks · Week 8 / Lab 8  
**Topic:** Network Layer / Routing Algorithms, Dijkstra's Shortest Path, Sink Trees & Forwarding Tables  
**System Implemented:** Graph Topology Modeler, Dijkstra Sink Tree Engine, Forwarding Table Generator, and Topology Visualizer in Python

---

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [Theoretical Foundations of Network Routing](#2-theoretical-foundations-of-network-routing)
   - [2.1 Routing vs. Forwarding](#21-routing-vs-forwarding)
   - [2.2 The Optimality Principle & Bellman's Theorem](#22-the-optimality-principle--bellmans-theorem)
   - [2.3 Mathematical Definition of a Sink Tree](#23-mathematical-definition-of-a-sink-tree)
   - [2.4 Link-State Routing Protocol (OSPF) Architecture](#24-link-state-routing-protocol-ospf-architecture)
3. [Dijkstra's Algorithm: Mathematical Formulation](#3-dijkstras-algorithm-mathematical-formulation)
   - [3.1 Vertex Set Partitioning ($S$ vs. $V \setminus S$)](#31-vertex-set-partitioning-s-vs-v-setminus-s)
   - [3.2 Edge Relaxation Invariant](#32-edge-relaxation-invariant)
   - [3.3 Time Complexity Analysis ($O(V^2)$ vs. $O((V+E)\log V)$)](#33-time-complexity-analysis-ov2-vs-ove-log-v)
4. [The Lab 8 Network Topology](#4-the-lab-8-network-topology)
   - [4.1 Node Set, Undirected Link Costs & Adjacency Representation](#41-node-set-undirected-link-costs--adjacency-representation)
   - [4.2 Verification of Non-Negative Edge Weight Constraint](#42-verification-of-non-negative-edge-weight-constraint)
5. [Step-by-Step Sink Tree Construction](#5-step-by-step-sink-tree-construction)
   - [5.1 Test Vector 1: Destination Sink = Router F](#51-test-vector-1-destination-sink--router-f)
   - [5.2 Test Vector 2: Destination Sink = Router A](#52-test-vector-2-destination-sink--router-a)
   - [5.3 Derivation of Router Forwarding Tables](#53-derivation-of-router-forwarding-tables)
6. [Part D: Deep-Dive Analysis & Theoretical Proofs](#6-part-d-deep-dive-analysis--theoretical-proofs)
   - [6.1 Proof of Loop-Free Routing from Tree Properties](#61-proof-of-loop-free-routing-from-tree-properties)
   - [6.2 Tie-Breaking Rules & Equal-Cost Multi-Path (ECMP)](#62-tie-breaking-rules--equal-cost-multi-path-ecmp)
   - [6.3 Failure Dynamics & Link-State Convergence](#63-failure-dynamics--link-state-convergence)
7. [Software Architecture & Python Implementation (`sink_tree.py`)](#7-software-architecture--python-implementation-sink_treepy)
8. [Comprehensive Viva & Exam Preparation Guide](#8-comprehensive-viva--exam-preparation-guide)

---

## 1. Executive Summary

In packet-switched network layer routing, routers must dynamically compute the most efficient, cost-effective paths across a complex graph of interconnected links. The foundational algorithm powering modern interior gateway routing protocols (such as OSPF and IS-IS) is **Dijkstra's Shortest Path Algorithm**.

In Lab 8, we model an undirected 6-router topology ($V = \{A, B, C, D, E, F\}$) with asymmetric link costs. We implement Dijkstra's algorithm to compute:
1. The **Sink Tree** rooted at any arbitrary destination router.
2. The exact **distance vectors** and cumulative path metrics from all sources to the sink.
3. The local **forwarding tables** (mapping destination to next-hop) across all nodes.
4. Proofs demonstrating why sink trees are inherently immune to routing loops.

```
+--------------------------------------------------------------------------------------------------+
|                                    NETWORK TOPOLOGY & SINK TREE (F)                              |
|                                                                                                  |
|   RAW TOPOLOGY:                                SINK TREE FOR DESTINATION F:                      |
|                                                                                                  |
|         (2)           (4)                                (2)           (4)                       |
|    A ───────── B ───────── D                       A ─────────► B ─────────► D                   |
|    │           │           │                       │                         │                   |
| (5)│        (1)│        (1)│ (2)                   │                         │ (2)               |
|    │           │           │                       │                         │                   |
|    C ───────── E ───────── F                       C ─────────► E ─────────► F (SINK)            |
|         (3)           (6)                                (3)           (1)                       |
|                                                    (Note: C routes via E, E via D, D to F)       |
+--------------------------------------------------------------------------------------------------+
```

---

## 2. Theoretical Foundations of Network Routing

### 2.1 Routing vs. Forwarding
- **Routing:** The network-wide, control-plane process of discovering the global network topology, exchanging link-state information, and calculating the optimal end-to-end paths between all source-destination pairs.
- **Forwarding:** The local, data-plane process executed by a router upon receiving a packet. The router inspects the packet's destination IP, performs a lookup in its local **forwarding table**, and switches the packet to the appropriate outgoing interface.

### 2.2 The Optimality Principle & Bellman's Theorem
The theoretical bedrock of shortest-path routing is **Bellman's Optimality Principle**:
> **Theorem:** If router $J$ lies on the optimal (shortest) path from router $I$ to router $K$, then the optimal path from router $J$ to router $K$ falls along that identical sub-path.

#### Proof by Contradiction:
Suppose there existed a shorter path from $J$ to $K$ than the sub-path used by the optimal route from $I$ to $K$. Then one could construct a shorter route from $I$ to $K$ by concatenating the sub-path $I \to J$ with this alternative shorter path $J \to K$. This contradicts the initial assumption that the original path $I \to K$ was optimal!

### 2.3 Mathematical Definition of a Sink Tree
A direct corollary of the Optimality Principle is that the set of optimal paths from all network sources to a single given destination (sink) forms a directed, spanning tree rooted at that destination:
$$\text{Sink Tree } T = (V, E_T), \quad \text{where } |E_T| = |V| - 1$$
Because a tree contains **no cycles (loops)**, packets forwarded along a sink tree are mathematically guaranteed to reach the destination in a finite number of hops without encountering routing loops!

### 2.4 Link-State Routing Protocol (OSPF) Architecture
In modern Link-State protocols (OSPF, Open Shortest Path First):
1. **Link-State Advertisements (LSAs):** Each router discovers its directly connected neighbors and the cost of each attached link.
2. **Reliable Flooding:** Routers flood LSAs across the entire autonomous system.
3. **Identical LSDB:** Every router constructs an identical **Link-State Database (LSDB)** representing the complete network graph.
4. **Local Dijkstra Execution:** Each router independently runs Dijkstra's algorithm with itself as the root to build its Shortest Path Tree (SPT) and populate its forwarding table.

---

## 3. Dijkstra's Algorithm: Mathematical Formulation

### 3.1 Vertex Set Partitioning ($S$ vs. $V \setminus S$)
Let the network graph be $G = (V, E)$, with non-negative edge costs $c(u, v) \ge 0$.
Dijkstra's algorithm partitions vertices into two disjoint sets:
- **Set $S$ (Permanent / Visited):** Vertices whose shortest distance to the sink has been finalized.
- **Set $V \setminus S$ (Tentative / Unvisited):** Vertices with tentative upper-bound distances.

### 3.2 Edge Relaxation Invariant
For a sink node $t$, initialize:
$$dist[t] = 0, \quad dist[u] = \infty \quad \forall u \ne t$$

At each step:
1. Select node $u \in V \setminus S$ with the minimum tentative distance $dist[u]$.
2. Move $u$ into permanent set $S$.
3. **Relax all incoming edges $(v, u) \in E$:**
   $$\text{If } dist[u] + c(v, u) < dist[v] \implies dist[v] = dist[u] + c(v, u), \quad parent[v] = u$$

The algorithm terminates when all vertices are added to $S$.

### 3.3 Time Complexity Analysis
- **Array / Matrix Implementation:** $O(V^2)$ — efficient for dense graphs ($E \approx V^2$).
- **Min-Heap / Priority Queue Implementation:** $O((V + E)\log V)$ — optimal for sparse computer networks ($E \ll V^2$).

---

## 4. The Lab 8 Network Topology

### 4.1 Node Set, Undirected Link Costs & Adjacency Representation
The network consists of $N = 6$ routers $V = \{A, B, C, D, E, F\}$ connected by 8 undirected links:

| Link | Cost $c(u, v)$ | Link | Cost $c(u, v)$ |
| :---: | :---: | :---: | :---: |
| **A – B** | 2 | **C – E** | 3 |
| **A – C** | 5 | **D – E** | 1 |
| **B – C** | 1 | **D – F** | 2 |
| **B – D** | 4 | **E – F** | 6 |

#### Adjacency List:
- **A:** $(B, 2), (C, 5)$
- **B:** $(A, 2), (C, 1), (D, 4)$
- **C:** $(A, 5), (B, 1), (E, 3)$
- **D:** $(B, 4), (E, 1), (F, 2)$
- **E:** $(C, 3), (D, 1), (F, 6)$
- **F:** $(D, 2), (E, 6)$

### 4.2 Verification of Non-Negative Edge Weight Constraint
All link costs are strictly positive integers ($c \ge 1$). Dijkstra's greedy choice property requires non-negative edge weights to guarantee that once a node enters permanent set $S$, its distance cannot be reduced by any future relaxation.

---

## 5. Step-by-Step Sink Tree Construction

### 5.1 Test Vector 1: Destination Sink = Router F

#### Step-by-Step Execution:
1. **Initial State:** $dist[F] = 0$, all others $\infty$. Permanent set $S = \emptyset$.
2. **Step 1:** Min node is **F** ($dist = 0$). Add to $S$.
   - Relax $(D, F)$: $dist[D] = \min(\infty, 0 + 2) = \mathbf{2}$, parent $= F$.
   - Relax $(E, F)$: $dist[E] = \min(\infty, 0 + 6) = \mathbf{6}$, parent $= F$.
3. **Step 2:** Min node in $V \setminus S$ is **D** ($dist = 2$). Add to $S$.
   - Relax $(B, D)$: $dist[B] = \min(\infty, 2 + 4) = \mathbf{6}$, parent $= D$.
   - Relax $(E, D)$: $dist[E] = \min(6, 2 + 1) = \mathbf{3}$ (Updated!), parent $= D$.
4. **Step 3:** Min node in $V \setminus S$ is **E** ($dist = 3$). Add to $S$.
   - Relax $(C, E)$: $dist[C] = \min(\infty, 3 + 3) = \mathbf{6}$, parent $= E$.
5. **Step 4:** Min node in $V \setminus S$: Tie between **B** ($dist = 6$) and **C** ($dist = 6$).
   - Pick **B** ($dist = 6$). Add to $S$.
     - Relax $(A, B)$: $dist[A] = \min(\infty, 6 + 2) = \mathbf{8}$, parent $= B$.
     - Check $(C, B)$: $6 + 1 = 7 > dist[C](6)$, no change.
   - Pick **C** ($dist = 6$). Add to $S$.
     - Check $(A, C)$: $6 + 5 = 11 > dist[A](8)$, no change.
6. **Step 5:** Min node in $V \setminus S$ is **A** ($dist = 8$). Add to $S$. All nodes finalized!

#### Final Distance Vector toward F:
$$\mathbf{A: 8, \quad B: 6, \quad C: 6, \quad D: 2, \quad E: 3, \quad F: 0}$$

#### Sink Tree Edges:
$$\{(A, B), (B, D), (C, E), (D, F), (E, D)\}$$

---

### 5.2 Test Vector 2: Destination Sink = Router A

Executing Dijkstra rooted at sink **A**:
- $A \to A = 0$
- $B \to A$: direct link cost $= \mathbf{2}$, parent $= A$.
- $C \to A$: via $B \to A \implies 1 + 2 = \mathbf{3}$, parent $= B$.
- $D \to A$: via $B \to A \implies 4 + 2 = \mathbf{6}$, parent $= B$.
- $E \to A$: via $C \to B \to A \implies 3 + 3 = \mathbf{6}$, parent $= C$.
- $F \to A$: via $D \to B \to A \implies 2 + 6 = \mathbf{8}$, parent $= D$.

#### Final Distance Vector toward A:
$$\mathbf{A: 0, \quad B: 2, \quad C: 3, \quad D: 6, \quad E: 6, \quad F: 8}$$

---

### 5.3 Derivation of Router Forwarding Tables

#### Forwarding Table for Destination F:
| Originating Router | Next Hop Toward F | Cumulative Cost | Path Traversed |
| :---: | :---: | :---: | :--- |
| **A** | **B** | 8 | $A \to B \to D \to F$ |
| **B** | **D** | 6 | $B \to D \to F$ |
| **C** | **E** | 6 | $C \to E \to D \to F$ |
| **D** | **F** | 2 | $D \to F$ |
| **E** | **D** | 3 | $E \to D \to F$ |
| **F** | *(Local Delivery)* | 0 | Direct (Destination Sink) |

---

## 6. Part D: Deep-Dive Analysis & Theoretical Proofs

### 6.1 Proof of Loop-Free Routing from Tree Properties
> **Theorem:** Under static link-state conditions where all routers compute forwarding tables using Dijkstra's algorithm, routing loops cannot exist.

#### Proof:
1. Every router independently runs Dijkstra with respect to the identical network graph $G$.
2. The union of the shortest paths from all sources to destination $F$ forms a directed spanning tree $T_F$.
3. By definition, a tree is an acyclic connected graph: it contains exactly $|V| - 1$ directed edges, and every node has a out-degree of exactly 1 (pointing to its unique parent toward the root).
4. Because a tree contains zero cycles, following the next-hop pointers from any arbitrary starting node produces a strictly monotonic path that terminates at root $F$ in at most $|V| - 1$ hops. Hence, loops are impossible.

---

### 6.2 Tie-Breaking Rules & Equal-Cost Multi-Path (ECMP)
In Step 4 of the Vector 1 derivation, nodes $B$ and $C$ both had tentative distance $6$:
- **Deterministic Tie-Breaking:** In single-path routing, ties must be broken deterministically across all routers (e.g. lowest alphabetical router ID or lowest interface number). Inconsistent tie-breaking between neighboring routers can create transient micro-loops!
- **Equal-Cost Multi-Path (ECMP):** In modern OSPF, when multiple shortest paths exist with identical total cost, routers retain both paths in the forwarding table and load-balance traffic hash-wise across them.

---

### 6.3 Failure Dynamics & Link-State Convergence
If link $D-F$ fails:
1. Routers $D$ and $F$ detect physical carrier loss.
2. They generate an updated LSA and flood it across the network.
3. Every router updates its local LSDB and re-runs Dijkstra's algorithm.
4. Path toward $F$ dynamically shifts to $E \to F$ (cost $3 + 6 = 9$), restoring end-to-end connectivity automatically.

---

## 7. Software Architecture & Python Implementation (`sink_tree.py`)

The script `sink_tree.py` provides:
- Network representation via adjacency dictionaries.
- Min-priority queue implementation of Dijkstra's algorithm.
- Automatic forwarding table generation and tabular printing.
- Graph visualization via NetworkX and Matplotlib (`plot_trees.py`), outputting `topology_and_sink_trees.png`.

---

## 8. Comprehensive Viva & Exam Preparation Guide

### Q1: What is the difference between a distance-vector protocol (RIP) and a link-state protocol (OSPF)?
**Answer:**
- In **Distance-Vector (RIP)**, routers share their entire routing table only with direct neighbors ("tells neighbors about the world"). Routers compute paths based on second-hand information without knowing the full topology, leading to count-to-infinity problems.
- In **Link-State (OSPF)**, routers flood only the state of their own directly connected links to all routers in the entire network ("tells the world about its neighbors"). Every router builds a complete, identical map of the network and independently runs Dijkstra's algorithm.

### Q2: Why does Dijkstra's algorithm fail if a graph contains negative-weight edges?
**Answer:** Dijkstra operates greedily: once a node $u$ is moved from tentative set to permanent set $S$, its distance is finalized and never revisited. If negative edge weights exist, a longer path with a negative edge could later reduce the distance to an already finalized node, rendering Dijkstra's greedy choice invalid. (The Bellman-Ford algorithm must be used instead for negative edge weights).

### Q3: What is the Optimality Principle, and what structure does it generate?
**Answer:** It states that if router $J$ is on the optimal path from router $I$ to router $K$, then the optimal path from $J$ to $K$ lies along that same path. This principle dictates that the set of all optimal paths from all sources to a single destination forms a directed acyclic tree rooted at the destination, known as the **Sink Tree**.

### Q4: How does a router convert a computed Shortest Path Tree into a Forwarding Table?
**Answer:** For each destination $D$, the router traverses the shortest path from itself toward $D$ in the tree. The very first intermediate node encountered on that path is recorded as the **Next Hop** in the router's local forwarding table.

---
*End of Lab 8 Report · Prepared for CS353 Computer Networks*

