# CS353 Computer Networks Lab — Lab 10 Report & Master Study Guide
# Network Layer: IP Routing Tables, Longest Prefix Match (LPM) & Multi-Hop Forwarding

**Course:** CS353: Computer Networks Laboratory  
**Department:** Computer Science and Engineering  
**Institution:** Indian Institute of Information Technology Guwahati (IIITG)  
**Experiment:** Lab 10 — IP Routing Tables, CIDR, Longest Prefix Match (LPM), and Multi-Hop Packet Forwarding  

---

## 1. Executive Summary & Architectural Overview

The **Network Layer** (OSI Layer 3 / Internet Layer in TCP/IP) provides end-to-end host-to-host packet delivery across heterogeneous internetworks. Unlike Layer 2 (Data Link Layer), which delivers frames within a single broadcast domain using 48-bit flat MAC addresses, Layer 3 utilizes a **hierarchical, topologically structured 32-bit IPv4 addressing system** (RFC 791, RFC 4632).

Every router in the Internet performs two distinctly decoupled operations:
1. **Routing (Control Plane):** The distributed process of discovering network topologies, exchanging reachability advertisements (via intra-domain protocols like OSPF/RIP and inter-domain protocols like BGP), and computing optimal paths to build the **Routing Information Base (RIB)**.
2. **Forwarding (Data Plane):** The local, per-packet hardware/software operation of inspecting the incoming packet's Destination IP address, querying the **Forwarding Information Base (FIB)**, and relaying the packet to the appropriate egress interface.

At the core of the forwarding plane is the **Longest Prefix Match (LPM)** algorithm. Because Classless Inter-Domain Routing (CIDR) allows route summarization, route aggregation, and multihomed subnetting, multiple routing table entries can match a single destination IP address simultaneously. The router must deterministically select the **most specific match** (the entry with the largest prefix length $/n$).

```
                      +---------------------------------------+
                      |       Routing Protocols (OSPF/BGP)   |  Control Plane
                      |       Routing Information Base (RIB)  |
                      +---------------------------------------+
                                          |
                                          v (Compiled into FIB)
+----------------+    +---------------------------------------+    +----------------+
| Incoming Packet| -> | Forwarding Engine:                    | -> | Outgoing Link  |  Data Plane
| Destination IP |    | Longest Prefix Match (LPM) on FIB     |    | (Next Hop)     |
+----------------+    +---------------------------------------+    +----------------+
```

This master report provides an exhaustive, mathematically rigorous, and code-verified study of:
- The transition from Classful addressing to CIDR and subnet mask mathematics.
- The bitwise verification rule `(D & M) == N`.
- Complete manual analysis of Numerical Exercise Table 1 with full bitwise breakdown.
- The Python implementation of `prefix_to_mask()`, `RoutingTable.add_route()`, and `RoutingTable.lookup()`.
- Multi-hop packet trace simulation across a 3-router topology (`R1 -> R2 -> R3`).
- Advanced hardware lookup architectures (Radix Trees, Patricia Tries, and TCAMs).
- Comprehensive viva-voce questions with model answers.

---

## 2. Theoretical & Mathematical Foundations

### 2.1 IPv4 Addressing Structure & Bitwise Notation
An IPv4 address is an unsigned 32-bit integer, conventionally formatted in dotted-decimal notation:

$$A = d_1 \cdot 2^{24} + d_2 \cdot 2^{16} + d_3 \cdot 2^8 + d_4, \quad \text{where } d_i \in [0, 255]$$

In binary representation:

$$A \in \{0, 1\}^{32}$$

### 2.2 Classful Addressing vs. Classless Inter-Domain Routing (CIDR)
Prior to 1993 (RFC 1519, updated by RFC 4632), the Internet utilized rigid address classes:
- **Class A:** Leading bit `0`, prefix `/8`, supporting $2^{24}-2 = 16,777,214$ hosts.
- **Class B:** Leading bits `10`, prefix `/16`, supporting $2^{16}-2 = 65,534$ hosts.
- **Class C:** Leading bits `110`, prefix `/24`, supporting $2^8-2 = 254$ hosts.

This rigid division caused catastrophic address allocation inefficiencies: an organization requiring 300 IP addresses was forced to request a Class B network ($65,534$ addresses), wasting over $99.5\%$ of the allocated space. By 1992, Class B address exhaustion threatened the viability of the Internet, while global routing tables exploded due to unaggregated Class C routes.

**CIDR (Classless Inter-Domain Routing)** abolished fixed boundary classes, introducing arbitrary prefix lengths $/n$ (where $0 \le n \le 32$):
- The first $n$ bits represent the **Network Prefix** (or Subnet ID).
- The remaining $32 - n$ bits represent the **Host Identifier**.

### 2.3 Subnet Mask Derivation
A subnet mask $M(n)$ of prefix length $n$ is a 32-bit word consisting of $n$ consecutive binary `1`s followed by $32 - n$ binary `0`s:

$$M(n) = \sum_{k=32-n}^{31} 2^k = (2^{32} - 1) - (2^{32-n} - 1)$$

In bitwise programming operations:

$$M(n) = \left( (0\text{xFFFFFFFF} \ll (32 - n)) \ \& \ 0\text{xFFFFFFFF} \right), \quad \text{for } 1 \le n \le 32$$

For $n = 0$:

$$M(0) = 0\text{x}00000000 \quad (\text{all 32 bits are zero})$$

> **Edge-Case Caution (Shift by 32):** In C, C++, and hardware ALUs, shifting a 32-bit integer left by 32 bits (`val << 32`) invokes **Undefined Behavior (UB)** according to ISO C standards. In Python, integers have arbitrary precision, so `0xFFFFFFFF << 32` produces a 64-bit value, which when masked with `0xFFFFFFFF` results in `0`. However, explicit conditional handling (`if prefix_length == 0: return 0`) is essential for portability and clarity.

### 2.4 The Bitwise Matching Rule
A destination IP address $D$ matches a routing table entry defined by network base address $N$ and prefix length $n$ (mask $M = M(n)$) if and only if:

$$D \ \& \ M = N$$

Where $\&$ denotes the bitwise AND operation.

### 2.5 Address Range, Subnet Size & Host Capacity
For any entry with network address $N$ and prefix length $n$:
1. **Total Number of IP Addresses:**

$$S_{\text{total}} = 2^{32 - n}$$

2. **Network Address (Base Address):**

$$N = D \ \& \ M$$

3. **Directed Broadcast Address:**

$$B = N \lor (\sim M) = N + (2^{32 - n} - 1)$$

4. **Usable Host IP Range:**
   - In standard LAN subnets ($n \le 30$): $[N + 1, B - 1]$, providing $2^{32 - n} - 2$ usable host addresses.
   - In point-to-point subnets ($n = 31$, RFC 3021): $[N, B]$, providing 2 usable addresses.
   - In host routes ($n = 32$): Exactly 1 address ($N$), usable for loopback or specific host routing.

### 2.6 The Longest Prefix Match (LPM) Rule
When an incoming packet's destination address $D$ matches multiple routing table entries $E_1, E_2, \dots, E_k$ with prefix lengths $n_1, n_2, \dots, n_k$, the router forwards the packet using the entry $E^*$ that satisfies:

$$E^* = \arg\max_{E_i \in \text{Matches}} \{ n_i \}$$

**Why LPM is necessary:**
- **Hierarchical Route Aggregation:** An upstream ISP can advertise a broad route `172.20.0.0/16` representing millions of subscribers.
- **Specific Subnet Exceptions:** A regional data center or specific department within that ISP can advertise a more specific route `172.20.4.0/22` or `172.20.4.128/25`.
- Routers worldwide forward general traffic toward the ISP's main backbone, but automatically divert traffic destined for the specific department toward its dedicated gateway without requiring the ISP to de-aggregate its entire `/16` block.

---

## 3. Analysis of Assignment Routing Table (Table 1)

The assignment provides the following routing table (Table 1):

| Entry ID | Destination Network | Prefix Length | Subnet Mask | Usable / Total IP Range | Next Hop |
|:---:|:---:|:---:|:---:|:---:|:---:|
| **E1** | `0.0.0.0` | `/0` | `0.0.0.0` | `0.0.0.0` – `255.255.255.255` | `198.51.100.1` (default route) |
| **E2** | `172.20.0.0` | `/16` | `255.255.0.0` | `172.20.0.0` – `172.20.255.255` | `10.10.10.2` |
| **E3** | `172.20.4.0` | `/22` | `255.255.252.0` | `172.20.4.0` – `172.20.7.255` | `10.10.10.3` |
| **E4** | `172.20.4.128` | `/25` | `255.255.255.128` | `172.20.4.128` – `172.20.4.255` | `10.10.10.4` |
| **E5** | `192.0.2.0` | `/24` | `255.255.255.0` | `192.0.2.0` – `192.0.2.255` | `directly connected (eth1)` |

### 3.1 Subnet Address Space & Range Derivations

#### Entry E1 (`0.0.0.0/0`) — Default Route:
- Mask: `0.0.0.0` ($0$ ones, $32$ zeros).
- For any 32-bit integer $D$: $D \ \& \ 0\text{x}00000000 = 0\text{x}00000000$.
- Matches every IPv4 address across the entire address space.

#### Entry E2 (`172.20.0.0/16`):
- Mask: `255.255.0.0` ($16$ ones, $16$ zeros).
- Checks whether the first two octets equal `172.20`.
- Range: `172.20.0.0` to `172.20.255.255` ($2^{16} = 65,536$ addresses).

#### Entry E3 (`172.20.4.0/22`):
- Mask: `255.255.252.0` ($22$ ones, $10$ zeros).
  - Octet 1: $11111111_2 = 255$
  - Octet 2: $11111111_2 = 255$
  - Octet 3: $11111100_2 = 252$ (6 network bits, 2 host bits)
  - Octet 4: $00000000_2 = 0$ (8 host bits)
- The network base for octet 3 is $4 = 00000100_2$.
- The 2 host bits in octet 3 can vary from $00_2$ to $11_2$ ($0$ to $3$ in decimal).
- Therefore, octet 3 spans from $4 + 0 = 4$ to $4 + 3 = 7$.
- Range: `172.20.4.0` to `172.20.7.255` ($2^{10} = 1,024$ addresses).

#### Entry E4 (`172.20.4.128/25`):
- Mask: `255.255.255.128` ($25$ ones, $7$ zeros).
  - Octets 1–3: $255.255.255$ ($24$ network bits)
  - Octet 4: $10000000_2 = 128$ ($1$ network bit, $7$ host bits)
- The network base for octet 4 is $128 = 10000000_2$.
- The 7 host bits in octet 4 can vary from $0000000_2$ to $1111111_2$ ($0$ to $127$ in decimal).
- Therefore, octet 4 spans from $128$ to $128 + 127 = 255$.
- Range: `172.20.4.128` to `172.20.4.255` ($2^7 = 128$ addresses).

#### Entry E5 (`192.0.2.0/24`):
- Mask: `255.255.255.0` ($24$ ones, $8$ zeros).
- Checks whether the first three octets equal `192.0.2`.
- Range: `192.0.2.0` to `192.0.2.255` ($2^8 = 256$ addresses).

---

## 4. Step-by-Step Manual Trace of Destination Addresses

We evaluate each destination IP address given in Part 1 against all entries in Table 1.

```
Subnet Hierarchy for 172.20.x.x:
[---------------------- E2: 172.20.0.0/16 ----------------------]
         [----------- E3: 172.20.4.0/22 -----------]
                   [-- E4: 172.20.4.128/25 --]
```

### Destination (a): `172.20.4.200`

1. **Test against E1 (`0.0.0.0/0`):**
   - $(172.20.4.200) \ \& \ 0.0.0.0 = 0.0.0.0$.
   - **MATCH** (Prefix length $= 0$).
2. **Test against E2 (`172.20.0.0/16`):**
   - $(172.20.4.200) \ \& \ 255.255.0.0 = 172.20.0.0$.
   - Target is `172.20.0.0`.
   - **MATCH** (Prefix length $= 16$).
3. **Test against E3 (`172.20.4.0/22`):**
   - Octet 3: $4 \ \& \ 252 = 00000100_2 \ \& \ 11111100_2 = 00000100_2 = 4$.
   - $(172.20.4.200) \ \& \ 255.255.252.0 = 172.20.4.0$.
   - Target is `172.20.4.0`.
   - **MATCH** (Prefix length $= 22$).
4. **Test against E4 (`172.20.4.128/25`):**
   - Octet 4: $200 \ \& \ 128 = 11001000_2 \ \& \ 10000000_2 = 10000000_2 = 128$.
   - $(172.20.4.200) \ \& \ 255.255.255.128 = 172.20.4.128$.
   - Target is `172.20.4.128`.
   - **MATCH** (Prefix length $= 25$).
5. **Test against E5 (`192.0.2.0/24`):**
   - Octet 1: $172 \ne 192$.
   - **NO MATCH**.

- **Matching Entries:** `0.0.0.0/0`, `172.20.0.0/16`, `172.20.4.0/22`, `172.20.4.128/25`
- **Longest Prefix Match:** `172.20.4.128/25` (Prefix length $= 25$)
- **Selected Next Hop:** `10.10.10.4`

---

### Destination (b): `172.20.4.5`

1. **Test against E1 (`0.0.0.0/0`):**
   - $(172.20.4.5) \ \& \ 0.0.0.0 = 0.0.0.0$.
   - **MATCH** (Prefix length $= 0$).
2. **Test against E2 (`172.20.0.0/16`):**
   - $(172.20.4.5) \ \& \ 255.255.0.0 = 172.20.0.0$.
   - Target is `172.20.0.0`.
   - **MATCH** (Prefix length $= 16$).
3. **Test against E3 (`172.20.4.0/22`):**
   - Octet 3: $4 \ \& \ 252 = 4$.
   - $(172.20.4.5) \ \& \ 255.255.252.0 = 172.20.4.0$.
   - Target is `172.20.4.0`.
   - **MATCH** (Prefix length $= 22$).
4. **Test against E4 (`172.20.4.128/25`):**
   - Octet 4: $5 \ \& \ 128 = 00000101_2 \ \& \ 10000000_2 = 0 \ne 128$.
   - **NO MATCH**.
5. **Test against E5 (`192.0.2.0/24`):**
   - Octet 1: $172 \ne 192$.
   - **NO MATCH**.

- **Matching Entries:** `0.0.0.0/0`, `172.20.0.0/16`, `172.20.4.0/22`
- **Longest Prefix Match:** `172.20.4.0/22` (Prefix length $= 22$)
- **Selected Next Hop:** `10.10.10.3`

---

### Destination (c): `172.20.9.9`

1. **Test against E1 (`0.0.0.0/0`):**
   - **MATCH** (Prefix length $= 0$).
2. **Test against E2 (`172.20.0.0/16`):**
   - $(172.20.9.9) \ \& \ 255.255.0.0 = 172.20.0.0$.
   - **MATCH** (Prefix length $= 16$).
3. **Test against E3 (`172.20.4.0/22`):**
   - Octet 3: $9 \ \& \ 252 = 00001001_2 \ \& \ 11111100_2 = 00001000_2 = 8 \ne 4$.
   - Note: The valid range for octet 3 in `172.20.4.0/22` is $[4, 7]$. Since $9 \notin [4, 7]$, it fails.
   - **NO MATCH**.
4. **Test against E4 (`172.20.4.128/25`):**
   - Octet 3 is $9 \ne 4$.
   - **NO MATCH**.
5. **Test against E5 (`192.0.2.0/24`):**
   - Octet 1: $172 \ne 192$.
   - **NO MATCH**.

- **Matching Entries:** `0.0.0.0/0`, `172.20.0.0/16`
- **Longest Prefix Match:** `172.20.0.0/16` (Prefix length $= 16$)
- **Selected Next Hop:** `10.10.10.2`

---

### Destination (d): `192.0.2.77`

1. **Test against E1 (`0.0.0.0/0`):**
   - **MATCH** (Prefix length $= 0$).
2. **Test against E2 (`172.20.0.0/16`):**
   - Octet 1: $192 \ne 172$.
   - **NO MATCH**.
3. **Test against E3 (`172.20.4.0/22`):**
   - **NO MATCH**.
4. **Test against E4 (`172.20.4.128/25`):**
   - **NO MATCH**.
5. **Test against E5 (`192.0.2.0/24`):**
   - $(192.0.2.77) \ \& \ 255.255.255.0 = 192.0.2.0$.
   - Target is `192.0.2.0`.
   - **MATCH** (Prefix length $= 24$).

- **Matching Entries:** `0.0.0.0/0`, `192.0.2.0/24`
- **Longest Prefix Match:** `192.0.2.0/24` (Prefix length $= 24$)
- **Selected Next Hop:** `directly connected (eth1)`

---

### Destination (e): `203.0.113.50`

1. **Test against E1 (`0.0.0.0/0`):**
   - **MATCH** (Prefix length $= 0$).
2. **Test against E2 (`172.20.0.0/16`):**
   - Octet 1: $203 \ne 172$.
   - **NO MATCH**.
3. **Test against E3 (`172.20.4.0/22`):**
   - **NO MATCH**.
4. **Test against E4 (`172.20.4.128/25`):**
   - **NO MATCH**.
5. **Test against E5 (`192.0.2.0/24`):**
   - Octet 1: $203 \ne 192$.
   - **NO MATCH**.

- **Matching Entries:** `0.0.0.0/0`
- **Longest Prefix Match:** `0.0.0.0/0` (Prefix length $= 0$)
- **Selected Next Hop:** `198.51.100.1` (default route)

---

### 4.1 Master Summary Table of Forwarding Decisions

| Packet | Destination IP | All Matching Entries | Winning Entry (LPM) | Matched Prefix Length | Next Hop / Egress Decision |
|:---|:---|:---|:---:|:---:|:---|
| **(a)** | `172.20.4.200` | `0.0.0.0/0`, `172.20.0.0/16`, `172.20.4.0/22`, `172.20.4.128/25` | `172.20.4.128/25` | `/25` | `10.10.10.4` |
| **(b)** | `172.20.4.5` | `0.0.0.0/0`, `172.20.0.0/16`, `172.20.4.0/22` | `172.20.4.0/22` | `/22` | `10.10.10.3` |
| **(c)** | `172.20.9.9` | `0.0.0.0/0`, `172.20.0.0/16` | `172.20.0.0/16` | `/16` | `10.10.10.2` |
| **(d)** | `192.0.2.77` | `0.0.0.0/0`, `192.0.2.0/24` | `192.0.2.0/24` | `/24` | `directly connected (eth1)` |
| **(e)** | `203.0.113.50` | `0.0.0.0/0` | `0.0.0.0/0` | `/0` | `198.51.100.1` (default route) |

---

## 5. Software Implementation Walkthrough (Task 1)

File: `task1_routing_table.py`

### 5.1 Fast Conversion Utilities: Struct and Socket

```python
import socket
import struct

def ip_to_int(ip_str: str) -> int:
    """Convert dotted-decimal string 'a.b.c.d' to 32-bit unsigned integer."""
    return struct.unpack("!I", socket.inet_aton(ip_str))[0]

def int_to_ip(ip_int: int) -> str:
    """Convert 32-bit unsigned integer to dotted-decimal string."""
    return socket.inet_ntoa(struct.pack("!I", ip_int))
```
- `socket.inet_aton(ip_str)` converts a C-string representation of an IPv4 address to 4 packed bytes in network byte order (Big-Endian).
- `struct.unpack("!I", ...)` interprets these 4 bytes as an unsigned 32-bit integer (`!I` = network endian, 4-byte unsigned int).
- This approach avoids manual string splitting, parsing, and arithmetic while remaining fully standards-compliant.

### 5.2 Subnet Mask Generator: `prefix_to_mask`

```python
def prefix_to_mask(prefix_length: int) -> int:
    """Return the 32-bit subnet mask (as an int) for a given CIDR prefix length.
    
    A /n mask has its top n bits set to 1 and remaining (32 - n) bits set to 0.
    For n = 0, shift by 32 is undefined/problematic, so we return 0 directly.
    """
    if prefix_length == 0:
        return 0
    return (0xFFFFFFFF << (32 - prefix_length)) & 0xFFFFFFFF
```
- If `prefix_length == 24`: $32 - 24 = 8$. `0xFFFFFFFF << 8` sets the lower 8 bits to `0`, producing `0xFFFFFF00` (`255.255.255.0`).
- If `prefix_length == 0`: Explicitly returns `0` (`0.0.0.0`), preventing edge-case bugs.

### 5.3 RoutingTable Implementation

```python
class RoutingTable:
    def __init__(self):
        self.routes = []

    def add_route(self, network: str, prefix_length: int, next_hop: str, label: str = ""):
        """Add one routing table entry with pre-masked network address."""
        mask = prefix_to_mask(prefix_length)
        # Protect against non-zero host bits passed by caller
        net_int = ip_to_int(network) & mask
        self.routes.append((net_int, prefix_length, mask, next_hop, label))

    def lookup(self, dest_ip: str):
        """Lookup dest_ip using Longest Prefix Match (LPM).
        
        Returns dict with next_hop, label, matched_prefix_length, or None.
        """
        dest_int = ip_to_int(dest_ip)
        best = None
        for net_int, prefix_length, mask, next_hop, label in self.routes:
            if (dest_int & mask) == net_int:
                if best is None or prefix_length > best[0]:
                    best = (prefix_length, next_hop, label)
        if best is None:
            return None
        return {
            "next_hop": best[1],
            "label": best[2],
            "matched_prefix_length": best[0]
        }
```

#### Defensive Sanitization in `add_route`:
If an administrator mistakenly configures a route like `172.20.4.200/22`, where host bits are non-zero, performing `ip_to_int(network) & mask` automatically clamps the stored network address to `172.20.4.0`. This ensures that subsequent `(dest_int & mask) == net_int` comparisons evaluate correctly.

---

## 6. Multi-Hop Forwarding Simulation (Task 2)

File: `task2_forwarding_simulation.py`

### 6.1 Network Topology & Addressing Plan

```
    HostA                                                      HostB
  192.168.1.0/24                                            192.168.2.0/24
        |                                                          |
     eth0 (.1)                                                  eth1 (.1)
       [R1] ---- 10.0.12.0/30 ---- [R2] ---- 10.0.23.0/30 ---- [R3]
     eth1 (.1)                 eth0 (.2) eth1 (.1)         eth0 (.2)
```

#### Point-to-Point `/30` Subnet Allocations:
1. **Link R1–R2 (`10.0.12.0/30`):**
   - Subnet Mask: `255.255.255.252` ($2$ host bits $\implies 4$ addresses).
   - Network: `10.0.12.0`
   - R1 Interface (`eth1`): `10.0.12.1`
   - R2 Interface (`eth0`): `10.0.12.2`
   - Broadcast: `10.0.12.3`
2. **Link R2–R3 (`10.0.23.0/30`):**
   - Network: `10.0.23.0`
   - R2 Interface (`eth1`): `10.0.23.1`
   - R3 Interface (`eth0`): `10.0.23.2`
   - Broadcast: `10.0.23.3`

### 6.2 Router FIB Configurations

#### Router R1:
- `192.168.1.0/24` $\implies$ `directly connected (R1-eth0)` (Host A subnet)
- `10.0.12.0/30` $\implies$ `directly connected (R1-eth1)` (Inter-router link)
- `0.0.0.0/0` $\implies$ Next Hop `10.0.12.2` (Default gateway toward R2)

#### Router R2:
- `10.0.12.0/30` $\implies$ `directly connected (R2-eth0)`
- `10.0.23.0/30` $\implies$ `directly connected (R2-eth1)`
- `192.168.1.0/24` $\implies$ Next Hop `10.0.12.1` (Toward R1)
- `192.168.2.0/24` $\implies$ Next Hop `10.0.23.2` (Toward R3)

#### Router R3:
- `192.168.2.0/24` $\implies$ `directly connected (R3-eth1)` (Host B subnet)
- `10.0.23.0/30` $\implies$ `directly connected (R3-eth0)` (Inter-router link)
- `0.0.0.0/0` $\implies$ Next Hop `10.0.23.1` (Default gateway toward R2)

### 6.3 Interface Ownership Mapping: `ip_owner`
In physical networks, a router knows which neighbor owns a next-hop IP by consulting its ARP table (RFC 826) over the local Layer 2 broadcast link. In our software simulation, `ip_owner` emulates this binding:

```python
ip_owner = {
    "10.0.12.1": "R1",
    "10.0.12.2": "R2",
    "10.0.23.1": "R2",
    "10.0.23.2": "R3",
}
```

### 6.4 The Multi-Hop Forwarding Loop: `trace_path`

```python
def trace_path(start_router: str, dest_ip: str, max_hops: int = 10):
    current = start_router
    path = []
    for _ in range(max_hops):
        result = routers[current].lookup(dest_ip)
        if result is None:
            path.append((current, "NO ROUTE -- packet dropped"))
            return path

        path.append((current, f"next_hop={result['next_hop']} (matched /{result['matched_prefix_length']})"))

        # Check for destination arrival (local subnet delivery)
        if result['next_hop'].startswith("directly connected"):
            return path

        # Resolve next-hop IP to the adjacent router entity
        current = ip_owner.get(result['next_hop'])
        if current is None:
            path.append(("---", "Unknown next hop router"))
            return path

    path.append(("---", "TTL exceeded / loop"))
    return path
```

### 6.5 Forward & Reverse Simulation Results

#### Forward Trace (Host A to Host B: `192.168.2.77` from R1):
1. **Hop 1 at R1:**
   - Lookup `192.168.2.77`.
   - Matches only `0.0.0.0/0`.
   - Decision: `next_hop=10.0.12.2 (matched /0)`.
   - `ip_owner["10.0.12.2"]` $\implies$ next router is **R2**.
2. **Hop 2 at R2:**
   - Lookup `192.168.2.77`.
   - Matches `192.168.2.0/24`.
   - Decision: `next_hop=10.0.23.2 (matched /24)`.
   - `ip_owner["10.0.23.2"]` $\implies$ next router is **R3**.
3. **Hop 3 at R3:**
   - Lookup `192.168.2.77`.
   - Matches `192.168.2.0/24`.
   - Decision: `next_hop=directly connected (R3-eth1) (matched /24)`.
   - Packet arrives on local LAN $\implies$ **Delivered**.

#### Reverse Trace (Host B to Host A: `192.168.1.50` from R3):
1. **Hop 1 at R3:**
   - Lookup `192.168.1.50`. Matches `0.0.0.0/0`.
   - Decision: `next_hop=10.0.23.1 (matched /0)`.
   - Next router: **R2**.
2. **Hop 2 at R2:**
   - Lookup `192.168.1.50`. Matches `192.168.1.0/24`.
   - Decision: `next_hop=10.0.12.1 (matched /24)`.
   - Next router: **R1**.
3. **Hop 3 at R1:**
   - Lookup `192.168.1.50`. Matches `192.168.1.0/24`.
   - Decision: `next_hop=directly connected (R1-eth0) (matched /24)`.
   - Packet arrives on local LAN $\implies$ **Delivered**.

---

## 7. Experimental Verification & Test Output

Both scripts were executed in the testing environment:

### Output of `python task1_routing_table.py`:
```text
172.20.4.200 -> {'next_hop': '10.10.10.4', 'label': 'R-C', 'matched_prefix_length': 25}
172.20.4.5 -> {'next_hop': '10.10.10.3', 'label': 'R-B', 'matched_prefix_length': 22}
172.20.9.9 -> {'next_hop': '10.10.10.2', 'label': 'R-A', 'matched_prefix_length': 16}
192.0.2.77 -> {'next_hop': 'directly connected (eth1)', 'label': 'direct', 'matched_prefix_length': 24}
203.0.113.50 -> {'next_hop': '198.51.100.1', 'label': 'default', 'matched_prefix_length': 0}

Self-check PASSED.
```

### Output of `python task2_forwarding_simulation.py`:
```text
('R1', 'next_hop=10.0.12.2 (matched /0)')
('R2', 'next_hop=10.0.23.2 (matched /24)')
('R3', 'next_hop=directly connected (R3-eth1) (matched /24)')

Self-check PASSED (R1 -> R2 -> R3 -> delivered).

Reverse direction (HostB -> HostA), starting at R3:
('R3', 'next_hop=10.0.23.1 (matched /0)')
('R2', 'next_hop=10.0.12.1 (matched /24)')
('R1', 'next_hop=directly connected (R1-eth0) (matched /24)')
```

---

## 8. Hardware Implementations & High-Speed Forwarding

In enterprise and core backbone routers handling $100\text{ Gbps}$ to $800\text{ Gbps}$ links, a software linear search over $1,000,000+$ routes (as seen in the modern global BGP table) is unviable. If a $64\text{-byte}$ packet arrives at $100\text{ Gbps}$, the router has only:

$$\Delta t = \frac{64 \times 8 \text{ bits}}{100 \times 10^9 \text{ bits/s}} = 5.12 \text{ nanoseconds}$$

to complete the entire lookup, update TTL, recompute the checksum, and cross the switch fabric. High-speed routers employ specialized data structures and hardware ALUs:

### 8.1 Software Data Structures: Radix Trees & Patricia Tries
- **Radix Tree:** A binary tree where each node represents a bit test ($0$ branch left, $1$ branch right). Traversal depth is bounded by address width ($W = 32$ for IPv4, $W = 128$ for IPv6). Lookup time is $O(W)$, independent of table size $R$.
- **Patricia Trie (Practical Algorithm to Retrieve Information Coded in Alphanumeric):** A compressed radix tree where one-child node sequences are collapsed, storing an explicit bit-skip index.
- **Multibit Trie (m-trie):** Inspects $k$ bits simultaneously (e.g., $k=4$ or $k=8$ bits per step), reducing tree depth from 32 steps to 4–8 memory accesses. Cisco Express Forwarding (CEF) utilizes a four-level 256-way multibit trie ($8-8-8-8$ stride).

```
                      (Root)
                     /      \
                   0/        \1
                 [Node]     [Node]
                 /    \       /   \
               0/      \1   0/     \1
             ...       ...  ...    ...
```

### 8.2 Hardware Lookups: TCAM (Ternary Content Addressable Memory)
Standard RAM takes an address as input and returns the data stored at that address in $O(1)$ time. **CAM (Content Addressable Memory)** does the reverse: it takes data as input and returns the memory location where that data matches.

**TCAM (Ternary CAM)** introduces a third "don't care" state ($X$):
- Each TCAM cell stores one of three states: `0`, `1`, or `X`.
- A route `172.20.4.0/22` is stored in TCAM as:
  $$10101100.00010100.000001XX.XXXXXXXX$$
- When destination `172.20.4.200` is presented on the comparand bus, **all TCAM entries evaluate their match conditions in parallel in a single clock cycle ($O(1)$ time)**.
- A priority encoder resolves multiple matching lines by selecting the entry with the lowest physical memory index (entries are sorted in memory by prefix length, with `/32` at the top and `/0` at the bottom).

| Technology | Data Structure | Lookup Time Complexity | Hardware / Memory Cost | Power Consumption |
|:---|:---|:---:|:---:|:---:|
| **Naive Software** | Unsorted Array | $O(R)$ | Low (Standard DRAM) | Negligible |
| **Tree Search** | Radix / Patricia Trie | $O(W) \approx 32$ memory hops | Moderate (SRAM) | Low |
| **Cisco CEF** | 256-way Multibit Trie | $O(W/k) \approx 4$ memory hops | High (Fast SRAM) | Moderate |
| **Hardware ASIC** | TCAM + Priority Encoder | $O(1)$ (Single clock cycle) | Very High ($8\times$ SRAM cost) | High ($15\text{ W} - 30\text{ W}$ per chip) |

---

## 9. Comprehensive Viva-Voce Questions & In-Depth Solutions

### Q1: Why was CIDR introduced, and how did it halt the collapse of the Internet routing system in 1993?
**Answer:** Prior to CIDR (RFC 1519/4632), IP addresses were assigned in fixed classes (A, B, C). Because Class C ($254$ hosts) was too small for most organizations and Class A was reserved for large entities, organizations overwhelmingly requested Class B blocks ($65,534$ hosts). This led to:
1. **Rapid Class B exhaustion:** Over $60\%$ of Class B blocks were consumed despite actual host utilization being under $10\%$.
2. **Routing table explosion:** ISPs forced to allocate hundreds of fragmented Class C blocks had to inject an individual routing entry for every single Class C block, threatening to overwhelm router memory limits.

CIDR solved both issues:
- **Variable-Length Subnet Masking (VLSM):** Organizations are allocated blocks matching their exact host requirements (e.g., `/22` for $1,024$ addresses, `/20` for $4,096$ addresses).
- **Route Aggregation (Supernetting):** Contiguous address blocks assigned to a single ISP can be aggregated into a single routing advertisement (e.g., 64 contiguous `/24` networks advertised upstream as a single `/18` prefix).

---

### Q2: Explain the technical difference between the Control Plane and Data Plane in modern routers.
**Answer:**
- **Control Plane:** Responsible for learning network topology, running dynamic routing algorithms (OSPF, IS-IS, BGP), and handling management protocols (SSH, SNMP). It builds and maintains the **Routing Information Base (RIB)**. The control plane operates in software on general-purpose CPUs and operates on timescales of milliseconds to seconds.
- **Data Plane (Forwarding Plane):** Responsible for switching individual packets from ingress interfaces to egress interfaces. It consults the **Forwarding Information Base (FIB)**, which is a pre-compiled, optimized lookup structure (such as an m-trie or TCAM table) derived directly from the RIB. The data plane is implemented in specialized hardware (ASICs, Network Processors, TCAMs) and operates on timescales of nanoseconds per packet.

---

### Q3: Why does the routing algorithm select the Longest Prefix Match rather than the shortest prefix or first matching entry?
**Answer:**
Hierarchical routing relies on **nested address spaces**:
- Broad prefixes (shorter prefixes, e.g., `/16`) represent large aggregate domains, regional networks, or entire ISPs.
- Specific prefixes (longer prefixes, e.g., `/25` or `/32`) represent localized subnets, specific server clusters, or multihomed customers that deviate from the aggregate route.

If a router selected the *shortest* prefix, it would match the default route (`/0`) or aggregate route (`/16`), misrouting packets to the general ISP backbone instead of the specific host subnet. If it selected the *first match*, routing decisions would depend arbitrarily on table ordering. The Longest Prefix Match guarantees that the packet is directed to the most specific, localized destination known to the routing system.

---

### Q4: How is the default route (`0.0.0.0/0`) represented mathematically, and why does every IPv4 address match it?
**Answer:**
The default route is specified by network IP `0.0.0.0` and prefix length $n = 0$.
The subnet mask for $n = 0$ is:

$$M(0) = 0\text{x}00000000 = 0.0.0.0$$

When evaluating the bitwise match condition for any 32-bit destination IP $D$:

$$D \ \& \ M(0) = D \ \& \ 0\text{x}00000000 = 0\text{x}00000000 = \text{Stored Network } (0.0.0.0)$$

Because the bitwise AND of any integer with 0 is identically 0, the equation $D \ \& \ M = N$ holds true for all $2^{32}$ possible IPv4 addresses. However, because its prefix length is $0$, any other matching route ($/1$ to $/32$) will have a longer prefix and take precedence under LPM. The default route is only chosen as the fallback when no specific entry matches.

---

### Q5: Why do point-to-point links between routers traditionally use `/30` subnets, and why does RFC 3021 recommend `/31` subnets?
**Answer:**
- **Traditional `/30` Subnets:** A `/30` prefix allocates $32 - 30 = 2$ host bits, yielding $2^2 = 4$ total IP addresses:
  - Base Address ($00_2$): Network ID (unusable for hosts).
  - First Host ($01_2$): Router A interface.
  - Second Host ($10_2$): Router B interface.
  - Broadcast Address ($11_2$): Directed Broadcast (unusable for hosts).
  While functional, 50% of the allocated address space ($2$ out of $4$ addresses) is wasted.
- **RFC 3021 (`/31` Subnets):** On dedicated point-to-point links, there is no shared broadcast domain, no other hosts exist, and packets can only travel to the single router at the other end. RFC 3021 permits `/31` prefixes ($1$ host bit $\implies 2$ addresses), where:
  - Address 0 is assigned to Router A.
  - Address 1 is assigned to Router B.
  Directed broadcast is eliminated, saving $50\%$ of point-to-point IPv4 address space across large networks.

---

### Q6: What happens when a router receives an IP packet for which there is NO matching entry and NO default route?
**Answer:**
If the destination IP does not match any route in the FIB and there is no default route (`0.0.0.0/0`):
1. The router **drops (discards)** the packet immediately.
2. The router generates an **ICMP Destination Unreachable** message (ICMP Type 3, Code 0: *Net Unreachable*, or Code 1: *Host Unreachable*) addressed to the packet's source IP address (RFC 792).
3. The original packet's IPv4 header and the first 8 bytes of its payload are embedded inside the ICMP message payload to allow the sending host to identify which application socket generated the failed packet.

---

### Q7: Can two entries in a valid routing table have identical prefix lengths and overlapping network addresses?
**Answer:**
In a standard deterministic Forwarding Information Base (FIB), two entries cannot have both the identical network address and identical prefix length unless **Equal-Cost Multi-Path (ECMP)** routing is enabled.
- If ECMP is configured, both entries have the same prefix length but point to different next-hop gateways across equal-cost links. The router hashes the packet 5-tuple (Source IP, Destination IP, Protocol, Source Port, Destination Port) to distribute traffic across the parallel paths while preserving packet ordering per flow.
- If ECMP is not configured and multiple routing protocols propose the same prefix, the router selects the entry with the lowest **Administrative Distance (AD)** (e.g., Connected = 0, Static = 1, eBGP = 20, OSPF = 110, RIP = 120).

---

### Q8: What is a "Host Route" (`/32`), and what operational purposes does it serve?
**Answer:**
A `/32` prefix has a mask of `255.255.255.255` ($32$ network bits, $0$ host bits). It matches exactly one specific IP address.
Operational use cases include:
1. **Loopback Interfaces:** Routers assign `/32` addresses to virtual loopback interfaces (`lo0`), serving as stable, un-flapping router IDs for OSPF, BGP peering sessions, and management access.
2. **Mobile IP & Host Mobility:** Directing traffic to an individual roaming host that has moved outside its native subnet.
3. **Blackholing / Null0 Routing:** Mitigating Distributed Denial of Service (DDoS) attacks by installing a `/32` route pointing to `Null0` (discard interface) for an attacked host IP, dropping malicious packets at the border router without impacting adjacent hosts on the same subnet.

---

### Q9: How does the shift from IPv4 to IPv6 (128-bit addresses) impact the computational complexity of LPM lookup?
**Answer:**
In IPv6 (RFC 8200), addresses are 128 bits wide:
- In software linear search, the lookup time is still bounded by $O(R)$, but 128-bit integer comparisons require four 32-bit registers (or two 64-bit registers), increasing memory bandwidth overhead.
- In binary Radix / Patricia Tries, worst-case tree traversal depth increases from $32$ steps to $128$ steps ($4\times$ increase in memory lookups).
- To maintain gigabit/terabit line rates, IPv6 implementations rely on deeper multibit tries ($k=8$ or $k=16$ bits per stride) or larger TCAMs with 128-bit comparison widths. Because TCAM power consumption scales linearly with bit-width, IPv6 forwarding engines require significantly more power and silicon die area than IPv4 engines.

---

### Q10: Trace how a routing loop occurs, and how the IPv4 Time-to-Live (TTL) field mitigates it.
**Answer:**
- **Loop Formation:** If Router R1's routing table directs packets for `192.168.2.0/24` to R2, and a misconfiguration or convergence transient causes R2's routing table to direct `192.168.2.0/24` back to R1, the two routers will bounce the packet back and forth indefinitely.
- **TTL Mitigation (RFC 791):**
  1. The sending host initializes the 8-bit IPv4 `TTL` field (e.g., 64, 128, or 255).
  2. Every router that forwards the packet must decrement `TTL` by at least 1.
  3. If a router decrements `TTL` to 0, it **must not** forward the packet. It drops the packet and transmits an **ICMP Time Exceeded** message (Type 11, Code 0) back to the sender.
  4. This ensures that looping packets consume link bandwidth for at most `TTL` hops before being purged from the network.

---

## 10. Summary Checklist for Viva & Lab Submissions

When reviewing Lab 10 materials for exams or lab assessments, ensure mastery of:
- [x] Subnet mask binary calculation: $M(n) = (0\text{xFFFFFFFF} \ll (32-n)) \ \& \ 0\text{xFFFFFFFF}$.
- [x] Handling the $n=0$ shift edge case for default routes.
- [x] Step-by-step bitwise verification: `(dest_ip & mask) == network`.
- [x] Determining subnet address ranges: Base address $N$ to Broadcast $N + (2^{32-n} - 1)$.
- [x] Longest Prefix Match tie-breaking rule: Pick the largest prefix length among all matching entries.
- [x] Multi-hop forwarding mechanics: Forwarding based strictly on local next-hop FIB entries without end-to-end path awareness.
- [x] Hardware acceleration mechanisms: Radix tries, Multibit tries (Cisco CEF), and TCAMs.

