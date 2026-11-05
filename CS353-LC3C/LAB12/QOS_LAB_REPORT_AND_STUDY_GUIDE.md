# CS353: Quality of Service (QoS) at a Router
## Comprehensive Lab Report, Theory Guide & Implementation Manual
**Course:** CS353 · Computer Networks · Week 11 / Lab 12  
**Topic:** Network Layer / Congestion Control and Quality of Service (QoS)  
**System Implemented:** Deterministic QoS Router with Admission Control, Traffic Policing, Traffic Shaping, and Weighted Fair Queuing (WFQ)

---

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [Theoretical Foundations of Quality of Service (QoS)](#2-theoretical-foundations-of-quality-of-service-qos)
   - [2.1 The Best-Effort Architecture Dilemma](#21-the-best-effort-architecture-dilemma)
   - [2.2 Four Fundamental QoS Performance Metrics](#22-four-fundamental-qos-performance-metrics)
   - [2.3 The Four Interconnected QoS Mechanisms](#23-the-four-interconnected-qos-mechanisms)
3. [System Architecture & Topology](#3-system-architecture--topology)
   - [3.1 Network Topology & Node Roles](#31-network-topology--node-roles)
   - [3.2 The Admitted Flows and Shared Capacity](#32-the-admitted-flows-and-shared-capacity)
4. [Part A: Admission Control (Parekh-Gallagher Model)](#4-part-a-admission-control-parekh-gallagher-model)
   - [4.1 Mathematical Formulation & GPS Theory](#41-mathematical-formulation--gps-theory)
   - [4.2 Step-by-Step Trace of Setup Requests](#42-step-by-step-trace-of-setup-requests)
   - [4.3 Comprehensive Answers to Part A Questions](#43-comprehensive-answers-to-part-a-questions)
5. [Part B: Traffic Policing (Token Bucket Drop)](#5-part-b-traffic-policing-token-bucket-drop)
   - [5.1 Token Bucket Mechanics & Parameters](#51-token-bucket-mechanics--parameters)
   - [5.2 Step-by-Step Packet Trace Execution](#52-step-by-step-packet-trace-execution)
   - [5.3 Comprehensive Answers to Part B Questions](#53-comprehensive-answers-to-part-b-questions)
   - [5.4 Comparison: Token Bucket vs. Leaky Bucket](#54-comparison-token-bucket-vs-leaky-bucket)
6. [Part C: Traffic Shaping (Token Bucket Buffer & Smooth)](#6-part-c-traffic-shaping-token-bucket-buffer--smooth)
   - [5.1 Shaper Architecture & Delay Derivations](#61-shaper-architecture--delay-derivations)
   - [6.2 Step-by-Step Packet Trace Execution](#62-step-by-step-packet-trace-execution)
   - [6.3 Comprehensive Answers to Part C Questions](#63-comprehensive-answers-to-part-c-questions)
   - [6.4 Side-by-Side Comparison: Policing vs. Shaping](#64-side-by-side-comparison-policing-vs-shaping)
7. [Part D: Packet Scheduling (Weighted Fair Queuing vs. FIFO)](#7-part-d-packet-scheduling-weighted-fair-queuing-vs-fifo)
   - [7.1 Generalized Processor Sharing (GPS) vs. Packetized WFQ](#71-generalized-processor-sharing-gps-vs-packetized-wfq)
   - [7.2 Mathematical Computation of Finish Numbers](#72-mathematical-computation-of-finish-numbers)
   - [7.3 Scheduling Orders: WFQ vs. FIFO](#73-scheduling-orders-wfq-vs-fifo)
   - [7.4 Comprehensive Answers to Part D Questions](#74-comprehensive-answers-to-part-d-questions)
8. [Software Architecture & Program Interface](#8-software-architecture--program-interface)
   - [8.1 Code Structure & Function Signatures](#81-code-structure--function-signatures)
   - [8.2 Automated Verification & Test Harness](#82-automated-verification--test-harness)
9. [Official Submission Deliverables (Direct Copy-Paste Ready)](#9-official-submission-deliverables-direct-copy-paste-ready)
10. [Comprehensive Viva & Exam Preparation Guide](#10-comprehensive-viva--exam-preparation-guide)

---

## 1. Executive Summary

In contemporary computer networks, the traditional **Best-Effort** service model treats all packets identically regardless of their real-time constraints, latency sensitivity, or commercial Service Level Agreements (SLAs). Under congestion, an unmanaged FIFO router allows aggressive or bursty flows to starve delay-sensitive flows, cause unpredictable jitter, and induce packet drops.

This laboratory implements a fully deterministic router capable of providing **Quality of Service (QoS)** by arbitrating a shared output link of capacity $C = 10\text{ Mbps}$ across multiple competing flows. Rather than modeling stochastic packet loss, this environment is deterministic, demonstrating how four core QoS building blocks operate in unison:

```
+-------------------------------------------------------------------------------------------------+
|                                 ROUTER R (QoS Controller)                                       |
|                                                                                                 |
|   Flow Setup Requests                                                                           |
|   ===================> [ 1. Admission Control ]                                                |
|                        Parekh-Gallagher Test: (W_i / ΣW)*C >= R_i                               |
|                                     |                                                           |
|                                     v (Admitted Weights: W_1=1, W_2=1, W_3=2)                   |
|   Incoming Traffic                  |                                                           |
|   ===================> [ 2. Traffic Policing ]  --> Drop non-conforming packets                 |
|                        (Token Bucket r, b)                                                      |
|                                     |                                                           |
|                        [ 3. Traffic Shaping  ]  --> Buffer & smooth excess traffic              |
|                        (Token Bucket r, b + Queue)                                              |
|                                     |                                                           |
|                                     v                                                           |
|                        [ 4. Packet Scheduling ]                                                 |
|                        Weighted Fair Queuing (WFQ): F_k = max(A_k, F_{k-1}) + L_k/w_i           |
|                                     |                                                           |
|                                     v Drains at C = 10 Mbps                                     |
|                               [ Shared Link ] ==========================> Receiver D            |
+-------------------------------------------------------------------------------------------------+
```

### Key Quantitative Results
1. **Admission Control:** Out of 4 sequential requests ($f_1, f_2, f_3, f_4$), flows $f_1, f_2, f_3$ are **admitted** (total weight $\Sigma W = 4$). Flow $f_4$ is **rejected** because its guaranteed rate is only $2.0\text{ Mbps}$ against its requested $3.0\text{ Mbps}$.
2. **Traffic Policing:** A burst of 6 packets at $t=0$ followed by packets at $t=5$ and $t=6$ is policed by a bucket of capacity $b=4$ and fill rate $r=1$. Exactly **6 packets pass** and **2 packets are dropped** (the 5th and 6th packets of the initial burst).
3. **Traffic Shaping:** Regulating the identical trace with a buffered shaper results in **zero dropped packets**. Packets 1–4 depart at $t=0$, packet 5 departs at $t=1$ (delay 1.0), packet 6 departs at $t=2$ (delay 2.0), and packets 7 & 8 depart immediately at $t=5$ and $t=6$ (delay 0.0).
4. **Packet Scheduling:** Under Weighted Fair Queuing, the packets from the three admitted flows finish in the exact order:
   $$\mathbf{A(8) \to C(10) \to B(11) \to E(14) \to F(16) \to G(19) \to D(20) \to H(28)}$$
   Under FIFO, the arrival order is $\mathbf{A \to B \to C \to D \to E \to F \to G \to H}$. WFQ prioritizes the weight-2 flow ($S_2$) and strictly isolates all flows from starvation.

---

## 2. Theoretical Foundations of Quality of Service (QoS)

### 2.1 The Best-Effort Architecture Dilemma
The original IP architecture operates on the principle of simplicity in the core and intelligence at the endpoints (the "end-to-end principle"). Under Best-Effort IP:
- Routers make no bandwidth reservations.
- Packets are scheduled strictly using First-In, First-Out (FIFO) queues.
- When queue buffers overflow, incoming packets are dropped (Tail Drop).

This creates severe limitations:
- **Starvation:** An aggressive UDP source can blast packets at link speed, filling the router buffer and starving conforming TCP or VoIP connections.
- **Uncontrolled Jitter:** Packets experience variable queuing delays depending on background cross-traffic, breaking real-time audio/video streaming.
- **Lack of SLAs:** Enterprise applications cannot receive minimum throughput guarantees.

### 2.2 Four Fundamental QoS Performance Metrics
QoS transforms an unmanaged network into a predictable communications channel governed by four measurable parameters:

| Metric | Definition | QoS Objective | Units |
| :--- | :--- | :--- | :--- |
| **Bandwidth (Throughput)** | The rate at which traffic from a flow is successfully delivered over the channel. | Guarantee a minimum reserved transmission rate $R_i$. | Mbps or bps |
| **Queuing Delay (Latency)** | Time spent by a packet waiting in router queues before transmission. | Bound the maximum queuing delay $\le D_{\max}$. | Milliseconds |
| **Jitter (Delay Variation)** | The statistical variance in packet end-to-end delay between consecutive packets. | Smooth packet arrival intervals to prevent audio/video buffer under-run. | Milliseconds |
| **Packet Loss Rate** | The percentage of packets discarded due to queue overflow or rate non-conformance. | Keep loss rate at $0\%$ or below a contracted threshold $\epsilon$. | Percentage / Ratio |

### 2.3 The Four Interconnected QoS Mechanisms
A comprehensive QoS router applies four complementary mechanisms at distinct stages:

```
[ Flow Arrival ] 
       │
       ▼
1. Admission Control ──(Rejects oversubscribing flows before admission)
       │
       ▼ [ Flow Admitted ]
2. Traffic Policing  ──(Detects contract violations; drops/marks non-conforming packets)
       │
       ▼ [ OR ]
3. Traffic Shaping   ──(Delays/buffers bursts to emit smooth, conforming traffic)
       │
       ▼
4. Packet Scheduling ──(Arbitrates shared link bandwidth; isolates competing flows)
       │
       ▼
[ Link Transmission ]
```

1. **Admission Control:** Acts as the network gatekeeper. Before a flow enters the network, it negotiates a traffic contract. The router checks whether admitting the new flow would compromise the guarantees promised to already active flows.
2. **Traffic Policing:** Operates at the network ingress to monitor traffic. If a flow sends faster than its contract specifies, the excess packets are immediately dropped or tagged with low drop-precedence. It has no memory (no queue).
3. **Traffic Shaping:** Operates at ingress or egress. Instead of dropping excess burst packets, it holds them in an internal queue and meters their transmission to match a specified average rate.
4. **Packet Scheduling:** Operates at the router output port. When multiple flows have packets simultaneously awaiting transmission over a shared bottleneck link, the scheduler chooses which packet to transmit next.

---

## 3. System Architecture & Topology

### 3.1 Network Topology & Node Roles
The system topology defined in the lab consists of four network entities:

```
  +--------------+
  | Source S1    |────┐
  | (Flows 1 & 2)|    │
  +--------------+    │
                      ├────► +--------------------------+                 +--------------+
                             | Router R                 |────(C=10 Mbps)─►| Receiver D   |
  +--------------+    ├────► | (Carries all 4 QoS Logic)|                 | (Passive Sink|
  | Source S2    |────┘      +--------------------------+                 +--------------+
  | (Flow 3)     |
  +--------------+
```

- **Source Host 1 ($S_1$):** Generates Flow 1 (weight 1) and Flow 2 (weight 1).
- **Source Host 2 ($S_2$):** Generates Flow 3 (weight 2).
- **Router ($R$):** The core intelligence node that executes Admission Control, Traffic Policing, Traffic Shaping, and Weighted Fair Queuing.
- **Receiver Host ($D$):** A passive traffic sink that receives conforming packets delivered across the output link.
- **Shared Output Link:** Has a fixed capacity $C = 10\text{ Mbps}$. No separate transmission medium or physical loss is modeled; contention is resolved deterministically by scheduling.

### 3.2 The Admitted Flows and Shared Capacity
The weights assigned during admission control represent the relative priority of each flow and directly dictate the bandwidth allocation in the scheduler:

| Flow Name | Source Host | Assigned Weight ($W_i$) | Normalized Share of Link | Minimum Guaranteed Bandwidth |
| :--- | :--- | :--- | :--- | :--- |
| **Flow 1** | $S_1$ | $1$ | $\frac{1}{1 + 1 + 2} = \frac{1}{4} = 25\%$ | $0.25 \times 10\text{ Mbps} = \mathbf{2.5\text{ Mbps}}$ |
| **Flow 2** | $S_1$ | $1$ | $\frac{1}{1 + 1 + 2} = \frac{1}{4} = 25\%$ | $0.25 \times 10\text{ Mbps} = \mathbf{2.5\text{ Mbps}}$ |
| **Flow 3** | $S_2$ | $2$ | $\frac{2}{1 + 1 + 2} = \frac{2}{4} = 50\%$ | $0.50 \times 10\text{ Mbps} = \mathbf{5.0\text{ Mbps}}$ |
| **Total** | — | $\mathbf{\Sigma W = 4}$ | $\mathbf{100\%}$ | $\mathbf{10.0\text{ Mbps}}$ |

---

## 4. Part A: Admission Control (Parekh-Gallagher Model)

### 4.1 Mathematical Formulation & GPS Theory
In 1993, Abhay Parekh and Robert Gallagher published their foundational theorem on Generalized Processor Sharing (GPS). Under GPS, if a set of flows $\mathcal{A}$ shares a link of total capacity $C$, and each flow $i \in \mathcal{A}$ has a weight $W_i$, then flow $i$ is guaranteed a minimum service rate:

$$\text{Guaranteed Rate}_i = \left( \frac{W_i}{\sum_{j \in \mathcal{A}} W_j} \right) \cdot C$$

#### The Admission Criterion
When a new flow $k$ requests admission with weight $W_k$ and requested minimum rate $R_k$, the router forms the candidate set:
$$\mathcal{A}' = \mathcal{A} \cup \{k\}, \quad \text{with total candidate weight } \Sigma W = \sum_{j \in \mathcal{A}'} W_j$$

Flow $k$ is **admissible if and only if**:
$$\forall j \in \mathcal{A}', \quad \left( \frac{W_j}{\Sigma W} \right) \cdot C \ge R_j$$

> **Critical QoS Invariant:** A new flow cannot be admitted if doing so causes **any** currently active flow's guaranteed rate to drop below its contracted rate $R_j$, nor if the new flow itself cannot receive its requested rate $R_k$.

### 4.2 Step-by-Step Trace of Setup Requests
The link capacity is $C = 10\text{ Mbps}$. Four flows request setup sequentially:

```
Request Stream:
1. Flow f1: Weight = 1, Rate R = 2 Mbps
2. Flow f2: Weight = 1, Rate R = 2 Mbps
3. Flow f3: Weight = 2, Rate R = 4 Mbps
4. Flow f4: Weight = 1, Rate R = 3 Mbps
```

#### Step 1: Flow $f_1$ requests admission ($W_1 = 1, R_1 = 2\text{ Mbps}$)
- Candidate set: $\mathcal{A}' = \{f_1\}$.
- Total weight: $\Sigma W = W_1 = 1$.
- Guaranteed rate for $f_1$:
  $$\text{Rate}_{f_1} = \left(\frac{1}{1}\right) \times 10 = 10.0\text{ Mbps} \ge 2.0\text{ Mbps} \quad \text{[PASSED]}$$
- **Decision:** **ADMITTED**.
- Active admitted set: $\{f_1\}$, Total weight $\Sigma W = 1$.

#### Step 2: Flow $f_2$ requests admission ($W_2 = 1, R_2 = 2\text{ Mbps}$)
- Candidate set: $\mathcal{A}' = \{f_1, f_2\}$.
- Total weight: $\Sigma W = 1 + 1 = 2$.
- Guaranteed rates:
  $$\text{Rate}_{f_1} = \left(\frac{1}{2}\right) \times 10 = 5.0\text{ Mbps} \ge 2.0\text{ Mbps} \quad \text{[PASSED]}$$
  $$\text{Rate}_{f_2} = \left(\frac{1}{2}\right) \times 10 = 5.0\text{ Mbps} \ge 2.0\text{ Mbps} \quad \text{[PASSED]}$$
- **Decision:** **ADMITTED**.
- Active admitted set: $\{f_1, f_2\}$, Total weight $\Sigma W = 2$.

#### Step 3: Flow $f_3$ requests admission ($W_3 = 2, R_3 = 4\text{ Mbps}$)
- Candidate set: $\mathcal{A}' = \{f_1, f_2, f_3\}$.
- Total weight: $\Sigma W = 1 + 1 + 2 = 4$.
- Guaranteed rates:
  $$\text{Rate}_{f_1} = \left(\frac{1}{4}\right) \times 10 = 2.5\text{ Mbps} \ge 2.0\text{ Mbps} \quad \text{[PASSED]}$$
  $$\text{Rate}_{f_2} = \left(\frac{1}{4}\right) \times 10 = 2.5\text{ Mbps} \ge 2.0\text{ Mbps} \quad \text{[PASSED]}$$
  $$\text{Rate}_{f_3} = \left(\frac{2}{4}\right) \times 10 = 5.0\text{ Mbps} \ge 4.0\text{ Mbps} \quad \text{[PASSED]}$$
- **Decision:** **ADMITTED**.
- Active admitted set: $\{f_1, f_2, f_3\}$, Total weight $\Sigma W = 4$.

#### Step 4: Flow $f_4$ requests admission ($W_4 = 1, R_4 = 3\text{ Mbps}$)
- Candidate set: $\mathcal{A}' = \{f_1, f_2, f_3, f_4\}$.
- Total weight: $\Sigma W = 1 + 1 + 2 + 1 = 5$.
- Guaranteed rates:
  $$\text{Rate}_{f_1} = \left(\frac{1}{5}\right) \times 10 = 2.0\text{ Mbps} \ge 2.0\text{ Mbps} \quad \text{[PASSED]}$$
  $$\text{Rate}_{f_2} = \left(\frac{1}{5}\right) \times 10 = 2.0\text{ Mbps} \ge 2.0\text{ Mbps} \quad \text{[PASSED]}$$
  $$\text{Rate}_{f_3} = \left(\frac{2}{5}\right) \times 10 = 4.0\text{ Mbps} \ge 4.0\text{ Mbps} \quad \text{[PASSED]}$$
  $$\text{Rate}_{f_4} = \left(\frac{1}{5}\right) \times 10 = \mathbf{2.0\text{ Mbps} < 3.0\text{ Mbps}} \quad \mathbf{[FAILED!]}$$
- **Decision:** **REJECTED**.
- Active admitted set remains: $\{f_1, f_2, f_3\}$, Total weight $\Sigma W = 4$.

### 4.3 Comprehensive Answers to Part A Questions

#### Question 3: Confirm that $f_1, f_2,$ and $f_3$ are admitted and $f_4$ is rejected.
**Confirmation:**
As calculated above, flows $f_1, f_2,$ and $f_3$ each receive a guaranteed rate strictly greater than or equal to their requested rates ($2.5 \ge 2$, $2.5 \ge 2$, and $5.0 \ge 4$). Flow $f_4$ requests $3.0\text{ Mbps}$ but would only be guaranteed $(1/5) \times 10 = 2.0\text{ Mbps}$. Thus, $f_4$ is rejected.

#### Question 4: State which flow's guarantee the rejection protects, and give the weight or rate $f_4$ would need to be admitted.
**Answer:**
1. **Which flow's guarantee the rejection protects:**
   - **$f_4$'s own contractual guarantee:** A QoS router guarantees that every admitted flow receives at least its requested rate. Admitting $f_4$ would violate the contract made with $f_4$ itself, as the router could only guarantee $2\text{ Mbps}$ against the $3\text{ Mbps}$ it demanded.
   - **The guarantees of active flows $f_1, f_2,$ and $f_3$:** The sum of requested rates for active flows is $R_1 + R_2 + R_3 = 2 + 2 + 4 = 8\text{ Mbps}$. On a link of capacity $C = 10\text{ Mbps}$, only $10 - 8 = 2\text{ Mbps}$ of spare capacity remains. If the router attempted to force $f_4$ into admission at $3\text{ Mbps}$ by giving it a higher weight (say $W_4 = 2$, yielding $\Sigma W = 6$), the rates of the other flows would drop:
     - $f_1$ would receive $(1/6) \times 10 = 1.67\text{ Mbps} < 2.0\text{ Mbps}$ (**Violation**)
     - $f_2$ would receive $(1/6) \times 10 = 1.67\text{ Mbps} < 2.0\text{ Mbps}$ (**Violation**)
     - $f_3$ would receive $(2/6) \times 10 = 3.33\text{ Mbps} < 4.0\text{ Mbps}$ (**Violation**)
     Therefore, rejecting $f_4$ directly protects **flows $f_1, f_2,$ and $f_3$** from SLA breaches.
2. **What rate or weight $f_4$ would need to be admitted:**
   - **Rate condition:** Keeping its assigned weight $W_4 = 1$, the total weight is $\Sigma W = 4 + 1 = 5$, giving $f_4$ a guaranteed rate of $(1/5) \times 10 = 2.0\text{ Mbps}$. Thus, $f_4$ would be admitted if it requested:
     $$\mathbf{R_4 \le 2.0\text{ Mbps}}$$
   - **Weight condition:** Can $f_4$ be admitted at $R_4 = 3.0\text{ Mbps}$ by simply increasing its weight $W_4$?
     **No!** Since $\sum_{i=1}^4 R_i = 2 + 2 + 4 + 3 = 11\text{ Mbps} > C = 10\text{ Mbps}$, the total requested rate exceeds physical link capacity. Under the conservation law of link capacity, no weight assignment can ever satisfy all four flows simultaneously. However, if unconstrained by other flows, $f_4$ alone would need $(W_4 / (4 + W_4)) \times 10 \ge 3 \implies 7 W_4 \ge 12 \implies W_4 \ge 1.714$, but this would break the others.

---

## 5. Part B: Traffic Policing (Token Bucket Drop)

### 5.1 Token Bucket Mechanics & Parameters
Traffic policing enforces traffic parameters at the packet level. It uses a **Token Bucket** model parameterized by:
- **Token Fill Rate ($r$):** The rate at which tokens are added to the bucket (representing the sustained, average allowable transmission rate).
- **Bucket Capacity ($b$):** The maximum number of tokens the bucket can hold (representing the allowable burst size).
- **Packet Cost ($L$):** The number of tokens consumed by each packet (typically proportional to packet length; here $L = 1\text{ token}$).

```
      Tokens arrive at rate r = 1 token / time unit
                  │
                  ▼
         ┌─────────────────┐
         │  TOKEN BUCKET   │  Capacity b = 4 tokens
         │  (Starts full)  │
         └────────┬────────┘
                  │ Tokens available?
                  ▼
         [ Conformance Test ]
          /                 \
    YES (Tokens >= L)     NO (Tokens < L)
        /                     \
       ▼                       ▼
  [ Forward Packet ]     [ DROP Packet ]
  (Consume L tokens)     (Zero buffering!)
```

#### Deterministic Parameters for the Lab:
- $r = 1\text{ token per time unit}$
- $b = 4\text{ tokens}$
- Initial state: Bucket starts full ($4\text{ tokens}$ at $t = 0$).
- Packet size: $L = 1\text{ token}$.
- Packet Arrival Trace:
  - Six packets arrive at $t = 0$ ($P_1, P_2, P_3, P_4, P_5, P_6$).
  - One packet arrives at $t = 5$ ($P_7$).
  - One packet arrives at $t = 6$ ($P_8$).

### 5.2 Step-by-Step Packet Trace Execution
At any packet arrival time $t$, with elapsed time $\Delta t = t - t_{\text{last}}$, the available tokens are updated:
$$\text{tokens} = \min(b, \text{tokens} + \Delta t \cdot r)$$

| Packet | Arrival ($t$) | $\Delta t$ | Tokens Before | Conformance Test ($T \ge 1$) | Action | Tokens After |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **$P_1$** | $0.0$ | $0.0$ | $4.0$ | $4.0 \ge 1.0 \implies$ True | **PASS** | $4.0 - 1.0 = \mathbf{3.0}$ |
| **$P_2$** | $0.0$ | $0.0$ | $3.0$ | $3.0 \ge 1.0 \implies$ True | **PASS** | $3.0 - 1.0 = \mathbf{2.0}$ |
| **$P_3$** | $0.0$ | $0.0$ | $2.0$ | $2.0 \ge 1.0 \implies$ True | **PASS** | $2.0 - 1.0 = \mathbf{1.0}$ |
| **$P_4$** | $0.0$ | $0.0$ | $1.0$ | $1.0 \ge 1.0 \implies$ True | **PASS** | $1.0 - 1.0 = \mathbf{0.0}$ |
| **$P_5$** | $0.0$ | $0.0$ | $0.0$ | $0.0 < 1.0 \implies$ False | **DROP** | $\mathbf{0.0}$ |
| **$P_6$** | $0.0$ | $0.0$ | $0.0$ | $0.0 < 1.0 \implies$ False | **DROP** | $\mathbf{0.0}$ |
| **$P_7$** | $5.0$ | $5.0$ | $\min(4, 0 + 5 \times 1) = 4.0$ | $4.0 \ge 1.0 \implies$ True | **PASS** | $4.0 - 1.0 = \mathbf{3.0}$ |
| **$P_8$** | $6.0$ | $1.0$ | $\min(4, 3 + 1 \times 1) = 4.0$ | $4.0 \ge 1.0 \implies$ True | **PASS** | $4.0 - 1.0 = \mathbf{3.0}$ |

**Summary Result:** Exactly **6 packets pass** and **2 packets drop**.

### 5.3 Comprehensive Answers to Part B Questions

#### Question 2: Confirm the result (first four pass, 5th and 6th dropped, packets at 5 and 6 pass).
**Confirmation:**
The numerical simulation exactly reproduces this sequence. $P_1, P_2, P_3, P_4$ pass at $t=0$; $P_5, P_6$ drop at $t=0$; $P_7$ at $t=5$ and $P_8$ at $t=6$ both pass.

#### Question 3: Explain why exactly two packets are dropped, in terms of the bucket capacity.
**Answer:**
The token bucket capacity is $b = 4$ tokens, and the bucket begins full. When an instantaneous burst of 6 packets arrives at time $t = 0$, the elapsed time between packets within the burst is zero ($\Delta t = 0$). Consequently, zero new tokens can accrue during the burst. 
Because each packet requires $L = 1$ token, the first 4 packets consume all 4 tokens accumulated in the bucket ($4 - 4 = 0$). When packets 5 and 6 are evaluated, the bucket has 0 tokens available. 
Because traffic policing operates **without a buffer**, it cannot queue non-conforming packets for future transmission. Therefore, the router immediately discards all packets exceeding the bucket's burst capacity $b$, which is exactly:
$$\text{Dropped Packets} = \text{Burst Size} - b = 6 - 4 = \mathbf{2\text{ packets}}.$$

### 5.4 Comparison: Token Bucket vs. Leaky Bucket

| Property | Leaky Bucket Algorithm | Token Bucket Algorithm |
| :--- | :--- | :--- |
| **Underlying Metaphor** | A bucket with a hole in the bottom that leaks water at a constant rate. | A bucket into which tokens are deposited at a constant rate up to capacity $b$. |
| **Output Rate** | Strictly constant (smooth, zero burstiness). | Variable: allows bursts up to bucket capacity $b$ at peak line rate. |
| **Burst Handling** | Eliminates bursts completely; flattens traffic. | Tolerates controlled bursts up to depth $b$, while enforcing average rate $r$. |
| **Token Conservation** | Packets wait in queue or overflow. | Idle periods accumulate tokens up to $b$ for future bursts. |
| **Primary Use Case** | ATM networks, strict CBR (Constant Bit Rate) traffic. | Modern IP networks (IntServ, DiffServ, RSVP, Linux `tc-tbf`). |

---

## 6. Part C: Traffic Shaping (Token Bucket Buffer & Smooth)

### 6.1 Shaper Architecture & Delay Derivations
Traffic shaping uses the same token bucket conformance parameters ($r = 1, b = 4$) as traffic policing, but introduces a **packet queue (buffer)**. 

```
                          Tokens arrive at rate r = 1
                                       │
                                       ▼
                              ┌─────────────────┐
                              │  TOKEN BUCKET   │
                              │  Capacity b = 4 │
                              └────────┬────────┘
                                       │
      Incoming Traffic                 │
  ========================> [ PACKET FIFO BUFFER ]
                                       │
                                       ▼
                       Tokens available in bucket?
                       ├── YES ──► Emit packet immediately (consume token)
                       └── NO  ──► Hold packet in buffer; emit when token arrives
```

When a packet arrives and insufficient tokens are present, rather than discarding the packet, the shaper buffers it until the required tokens accrue at rate $r$.

#### Mathematical Recurrence for Shaper Release Times:
Let $t_{\text{curr}}$ be the shaper's clock, initialized to $0.0$, and available tokens $= b$.
For a packet arriving at time $t_{\text{arr}}$ with size $L$:
1. If $t_{\text{arr}} > t_{\text{curr}}$, time has advanced:
   $$\text{tokens} = \min(b, \text{tokens} + (t_{\text{arr}} - t_{\text{curr}}) \cdot r), \quad t_{\text{curr}} = t_{\text{arr}}$$
2. If $\text{tokens} \ge L$:
   $$\text{tokens} \leftarrow \text{tokens} - L, \quad t_{\text{release}} = t_{\text{curr}}$$
3. If $\text{tokens} < L$:
   $$\text{needed} = L - \text{tokens}, \quad \text{wait time} = \frac{\text{needed}}{r}$$
   $$t_{\text{curr}} \leftarrow t_{\text{curr}} + \text{wait time}, \quad \text{tokens} \leftarrow 0.0, \quad t_{\text{release}} = t_{\text{curr}}$$
4. The queuing delay experienced by the packet is:
   $$\text{Delay} = t_{\text{release}} - t_{\text{arr}}$$

### 6.2 Step-by-Step Packet Trace Execution
Using the same trace ($6$ packets at $t=0$, $1$ at $t=5$, $1$ at $t=6$):

| Packet | Arrival ($t_{\text{arr}}$) | Available Tokens | Action | Release Time ($t_{\text{rel}}$) | Delay ($t_{\text{rel}} - t_{\text{arr}}$) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **$P_1$** | $0.0$ | $4.0 \ge 1$ | Transmit immediately; tokens left = $3.0$ | $\mathbf{0.0}$ | $\mathbf{0.0}$ |
| **$P_2$** | $0.0$ | $3.0 \ge 1$ | Transmit immediately; tokens left = $2.0$ | $\mathbf{0.0}$ | $\mathbf{0.0}$ |
| **$P_3$** | $0.0$ | $2.0 \ge 1$ | Transmit immediately; tokens left = $1.0$ | $\mathbf{0.0}$ | $\mathbf{0.0}$ |
| **$P_4$** | $0.0$ | $1.0 \ge 1$ | Transmit immediately; tokens left = $0.0$ | $\mathbf{0.0}$ | $\mathbf{0.0}$ |
| **$P_5$** | $0.0$ | $0.0 < 1$ | Buffer! Wait $1/r = 1.0$ unit for 1 token | $\mathbf{1.0}$ | $\mathbf{1.0}$ |
| **$P_6$** | $0.0$ | $0.0 < 1$ | Buffer! Wait next token at $t = 1.0 + 1.0$ | $\mathbf{2.0}$ | $\mathbf{2.0}$ |
| **$P_7$** | $5.0$ | $0 + 3 \times 1 = 3.0$ | Transmit immediately; tokens left = $2.0$ | $\mathbf{5.0}$ | $\mathbf{0.0}$ |
| **$P_8$** | $6.0$ | $2 + 1 \times 1 = 3.0$ | Transmit immediately; tokens left = $2.0$ | $\mathbf{6.0}$ | $\mathbf{0.0}$ |

**Summary Result:** All **8 packets are successfully delivered**. Zero packets are dropped.

### 6.3 Comprehensive Answers to Part C Questions

#### Question 2: Confirm release times.
**Confirmation:**
Packets $P_1, P_2, P_3, P_4$ leave at $t = 0$; packet $P_5$ leaves at $t = 1$; packet $P_6$ leaves at $t = 2$; packets $P_7$ and $P_8$ leave at $t = 5$ and $t = 6$. Zero packet loss occurs.

#### Question 3: Report delay for each packet, compare with Part B, and state the single difference.
**Answer:**
1. **Delays Experienced in Shaping:**
   - Packets 1 to 4: Delay = $0.0$ time units.
   - Packet 5: Delay = $1.0$ time unit.
   - Packet 6: Delay = $2.0$ time units.
   - Packets 7 and 8: Delay = $0.0$ time units.
2. **Comparison with Part B (Policing):**
   - In Part B (Policing), packets 5 and 6 suffered **catastrophic packet loss** (dropped completely; equivalent to infinite delay). The remaining 6 packets experienced zero delay.
   - In Part C (Shaping), packet loss was **zero ($0\%$)**. All 8 packets were delivered, with packets 5 and 6 experiencing brief, bounded queuing delays ($1.0$ and $2.0$ units) while waiting for tokens to regenerate.
3. **The Single Fundamental Difference:**
   The single architectural difference is the **presence of a Packet Buffer (Queue)**.
   - A **policer has NO buffer**: non-conforming packets are discarded immediately upon arrival.
   - A **shaper HAS a buffer**: non-conforming packets are queued and delayed until tokens become available.

### 6.4 Side-by-Side Comparison: Policing vs. Shaping

```
Traffic Arrival Pattern: [P1, P2, P3, P4, P5, P6 at t=0] ───────► [P7 at t=5] ──► [P8 at t=6]

POLICING Output:         [P1, P2, P3, P4 at t=0] ───────────────► [P7 at t=5] ──► [P8 at t=6]
                         (P5 & P6 DROPPED)

SHAPING Output:          [P1-P4 at t=0] ─► [P5 at t=1] ─► [P6 at t=2] ─► [P7 at t=5] ─► [P8 at t=6]
                         (NO PACKETS DROPPED; P5 & P6 smoothed into conforming output)
```

| Dimension | Traffic Policing (Part B) | Traffic Shaping (Part C) |
| :--- | :--- | :--- |
| **Primary Action on Excess** | Discards (or marks) non-conforming packets. | Buffers non-conforming packets until conforming. |
| **Packet Buffer** | No buffer. | Requires memory/queue buffer. |
| **Packet Loss** | High during bursts ($25\%$ in this experiment). | Zero (assuming sufficient buffer capacity). |
| **Introduced Latency** | None (packets pass immediately or die). | Introduces queuing delay to smooth bursts. |
| **Jitter Impact** | Unaltered for passing traffic. | Decreases downstream jitter by pacing packets. |
| **Typical Placement** | Ingress of ISP networks / SLA policing. | Egress of customer edge routers / egress ports. |

---

## 7. Part D: Packet Scheduling (Weighted Fair Queuing vs. FIFO)

### 7.1 Generalized Processor Sharing (GPS) vs. Packetized WFQ
Generalized Processor Sharing (GPS) is an idealized fluid-flow scheduling discipline where all active flows transmit simultaneously, each receiving a share of the link proportional to its weight:

$$\text{Share}_i = \frac{w_i}{\sum_{j \in \text{Active}} w_j}$$

However, real networks cannot transmit fluid fractions of packets simultaneously; packets are discrete units that must be transmitted serially without preemption.

**Weighted Fair Queuing (WFQ)** emulates GPS on discrete packets by assigning each arriving packet a **virtual finish number ($F$)**, representing the time the packet would have completed transmission under the idealized GPS model. The router then serves packets across all flows in **increasing order of finish number**.

#### The Finish Number Equation:
For packet $k$ of flow $i$ with arrival time $A_k$, packet length $L_k$, and flow weight $w_i$:

$$F_k = \max(A_k, F_{k-1}) + \frac{L_k}{w_i}$$

where $F_{k-1}$ is the finish number of the previous packet in the **same flow** (with $F_0 = 0$).
- $\max(A_k, F_{k-1})$ represents the virtual start time of packet $k$. If the flow was previously idle, it starts at its arrival time $A_k$. If the flow has backlogged packets, packet $k$ cannot start until packet $k-1$ completes.
- $\frac{L_k}{w_i}$ represents the normalized transmission duration. Higher weight $w_i$ reduces this term, allowing the packet to complete earlier in virtual time.

### 7.2 Mathematical Computation of Finish Numbers
Carrying over the weights from Part A:
- **Flow 1:** weight $w_1 = 1$
- **Flow 2:** weight $w_2 = 1$
- **Flow 3:** weight $w_3 = 2$

```
Packet Specifications:
Flow 1 (w=1): A(arrival=0, len=8), F(arrival=10, len=6)
Flow 2 (w=1): B(arrival=5, len=6), D(arrival=8, len=9), H(arrival=20, len=8)
Flow 3 (w=2): C(arrival=5, len=10), E(arrival=8, len=8), G(arrival=11, len=10)
```

#### Detailed Flow-by-Flow Calculations:

1. **Flow 1 ($w_1 = 1$):**
   - **Packet A:** Arrival $A = 0$, Length $L = 8$.
     $$F_A = \max(0, 0) + \frac{8}{1} = 0 + 8 = \mathbf{8.0}$$
   - **Packet F:** Arrival $A = 10$, Length $L = 6$. Previous finish in Flow 1 $= F_A = 8.0$.
     $$F_F = \max(10, 8.0) + \frac{6}{1} = 10 + 6 = \mathbf{16.0}$$

2. **Flow 2 ($w_2 = 1$):**
   - **Packet B:** Arrival $A = 5$, Length $L = 6$.
     $$F_B = \max(5, 0) + \frac{6}{1} = 5 + 6 = \mathbf{11.0}$$
   - **Packet D:** Arrival $A = 8$, Length $L = 9$. Previous finish in Flow 2 $= F_B = 11.0$.
     $$F_D = \max(8, 11.0) + \frac{9}{1} = 11.0 + 9 = \mathbf{20.0}$$
   - **Packet H:** Arrival $A = 20$, Length $L = 8$. Previous finish in Flow 2 $= F_D = 20.0$.
     $$F_H = \max(20, 20.0) + \frac{8}{1} = 20 + 8 = \mathbf{28.0}$$

3. **Flow 3 ($w_3 = 2$):**
   - **Packet C:** Arrival $A = 5$, Length $L = 10$.
     $$F_C = \max(5, 0) + \frac{10}{2} = 5 + 5 = \mathbf{10.0}$$
   - **Packet E:** Arrival $A = 8$, Length $L = 8$. Previous finish in Flow 3 $= F_C = 10.0$.
     $$F_E = \max(8, 10.0) + \frac{8}{2} = 10.0 + 4 = \mathbf{14.0}$$
   - **Packet G:** Arrival $A = 11$, Length $L = 10$. Previous finish in Flow 3 $= F_E = 14.0$.
     $$F_G = \max(11, 14.0) + \frac{10}{2} = 14.0 + 5 = \mathbf{19.0}$$

### 7.3 Scheduling Orders: WFQ vs. FIFO

#### Master Packet Comparison Table:

| Packet | Flow | Weight ($w$) | Arrival ($A$) | Length ($L$) | Start Virtual | Finish Number ($F$) | WFQ Rank | FIFO Rank |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **A** | Flow 1 | 1 | 0 | 8 | 0 | **8.0** | **1** | **1** |
| **C** | Flow 3 | 2 | 5 | 10 | 5 | **10.0** | **2** | **3** |
| **B** | Flow 2 | 1 | 5 | 6 | 5 | **11.0** | **3** | **2** |
| **E** | Flow 3 | 2 | 8 | 8 | 10 | **14.0** | **4** | **5** |
| **F** | Flow 1 | 1 | 10 | 6 | 10 | **16.0** | **5** | **6** |
| **G** | Flow 3 | 2 | 11 | 10 | 14 | **19.0** | **6** | **7** |
| **D** | Flow 2 | 1 | 8 | 9 | 11 | **20.0** | **7** | **4** |
| **H** | Flow 2 | 1 | 20 | 8 | 20 | **28.0** | **8** | **8** |

#### Comparison of Transmission Sequences:
- **Weighted Fair Queuing (WFQ) Order:**
  $$\mathbf{A \;\longrightarrow\; C \;\longrightarrow\; B \;\longrightarrow\; E \;\longrightarrow\; F \;\longrightarrow\; G \;\longrightarrow\; D \;\longrightarrow\; H}$$
- **First-In First-Out (FIFO) Order:**
  $$\mathbf{A \;\longrightarrow\; B \;\longrightarrow\; C \;\longrightarrow\; D \;\longrightarrow\; E \;\longrightarrow\; F \;\longrightarrow\; G \;\longrightarrow\; H}$$

### 7.4 Comprehensive Answers to Part D Questions

#### Question 2: Confirm the finish numbers and output order.
**Confirmation:**
The calculated finish numbers are:
- A: $8$
- C: $10$
- B: $11$
- E: $14$
- F: $16$
- G: $19$
- D: $20$
- H: $28$

Sorting these strictly in increasing order yields the confirmed sequence:
$$\mathbf{A, C, B, E, F, G, D, H}$$

#### Question 4a: Compare the two orders and explain how the weight-2 flow is served.
**Answer:**
1. **Service of Flow 3 (Weight 2):**
   In WFQ, each packet's finish number is incremented by $\frac{L}{w}$. Because Flow 3 has weight $w=2$ (double that of Flow 1 and Flow 2), its effective virtual duration per byte is halved ($\frac{L}{2}$ instead of $\frac{L}{1}$).
   - **Packet C vs. Packet B:** Both arrive at $t = 5$. Packet C has a large length of 10, while B has a shorter length of 6. Under FIFO, B would be served before or alongside C based on tie-breaking. Under WFQ, Packet C's virtual transmission time is $10/2 = 5$, giving $F_C = 10$, whereas B's is $6/1 = 6$, giving $F_B = 11$. Thus, **Packet C is scheduled BEFORE Packet B!**
   - **Packet E vs. Packet D:** Both arrive at $t = 8$. Under FIFO, Packet D arrives at $t=8$ and would be served at rank 4. Under WFQ, Packet E has finish number $14.0$, whereas Packet D has finish number $20.0$. Thus, Packet E jumps ahead of both Packet F (finish 16) and Packet D (finish 20).
   - **Packet G vs. Packet D:** Packet G arrives later at $t = 11$, yet because of Flow 3's weight 2, $F_G = 19.0 < F_D = 20.0$. Packet G is transmitted before Packet D!
2. **Outcome:**
   WFQ grants Flow 3 exactly **50% of the link capacity**, transmitting its packets at twice the frequency of Flow 1 and Flow 2 packets, completely independent of arrival packet sizes.

#### Question 4b: How does Weighted Fair Queuing protect a flow from being starved by another?
**Answer:**
Under FIFO, a single malicious or aggressive flow that floods packets can completely fill the router's queue, forcing the scheduler to transmit its packets back-to-back and starving conforming flows of bandwidth.

WFQ prevents starvation through **strict flow isolation**:
1. **Independent Per-Flow Finish Progress:**
   A flow's finish number formula contains $\max(\text{arrival}, F_{\text{prev}})$. If an aggressive flow pumps back-to-back packets into the queue, its $F_{\text{prev}}$ keeps compounding far into the virtual future:
   $$F_k = F_{k-1} + \frac{L_k}{w_{\text{aggressive}}}$$
   Its packets receive increasingly huge finish numbers (e.g. $F = 50, 80, 120\dots$).
2. **Immediate Service for Conforming / Idle Flows:**
   When an idle, well-behaved flow suddenly sends a packet at time $t_{\text{arr}}$, its finish number is calculated using its fresh arrival time:
   $$F_{\text{new}} = t_{\text{arr}} + \frac{L}{w}$$
   Because its virtual clock has not advanced into the future, its finish number will be significantly smaller than the backlogged packets of the abusive flow.
3. **Guaranteed Minimum Service Rate:**
   The scheduler immediately switches to transmitting the conforming flow's packet. Mathematically, Parekh and Gallagher proved that under WFQ, every active flow $i$ is guaranteed a deterministic minimum service rate of:
   $$\text{Rate}_i \ge \left( \frac{w_i}{\sum_j w_j} \right) \cdot C$$
   regardless of the arrival patterns or misbehavior of any other flow. Therefore, **starvation is mathematically impossible**.

---

## 8. Software Architecture & Program Interface

### 8.1 Code Structure & Function Signatures
The complete Python source file (`qos_router.py`) implements the exact functional interfaces specified in the assignment appendix:

```python
# Appendix Interface 1: Admission Control
def admit(requests: List[Dict[str, Any]], C: float) -> List[Dict[str, Any]]:
    """Applies the Parekh-Gallagher test sequentially over incoming flow setup requests."""

# Appendix Interface 2: Traffic Policing
def police(trace: List[float], r: float, b: float, packet_size: float = 1.0) -> List[Dict[str, Any]]:
    """Polices packet trace over a token bucket; drops non-conforming packets immediately."""

# Appendix Interface 3: Traffic Shaping
def shape(trace: List[float], r: float, b: float, packet_size: float = 1.0) -> List[Dict[str, Any]]:
    """Shapes packet trace over a token bucket with FIFO queue; releases when tokens accrue."""

# Appendix Interface 4: Packet Scheduling
def wfq(flows: Dict[str, Dict[str, Any]]) -> Tuple[Dict[str, float], List[str]]:
    """Computes WFQ finish numbers and returns output transmission order."""

def fifo(flows: Dict[str, Dict[str, Any]]) -> List[str]:
    """Returns FIFO arrival order for the given flows and packets."""
```

### 8.2 Automated Verification & Test Harness
Both Python (`qos_router.py`) and C++ (`qos_router.cpp`) scripts feature built-in assertion tests that validate every calculation against the lab specifications:
- `assert decisions[3]['admitted'] is False` (Flow $f_4$ rejection verified)
- `assert [p['action'] for p in police_results] == ['PASS','PASS','PASS','PASS','DROP','DROP','PASS','PASS']` (Policing verified)
- `assert [s['release_time'] for s in shape_results] == [0, 0, 0, 0, 1, 2, 5, 6]` (Shaping verified)
- `assert wfq_order == ['A', 'C', 'B', 'E', 'F', 'G', 'D', 'H']` (WFQ sequence verified)

To execute the verification harness:
```bash
python qos_router.py
```

---

## 9. Official Submission Deliverables (Direct Copy-Paste Ready)

This section provides the exact written responses required by the assignment handout.

### 9.1 Source Files & Program Output
- **Python Source Code:** `qos_router.py`
- **C++ Source Code:** `qos_router.cpp`
- **Reproduced Program Output:** `program_output.txt`

### 9.2 Written Answers

#### Part A: Admission Control
> **Question:** State which flow's guarantee the rejection protects, and give the weight or rate $f_4$ would need to be admitted.
>
> **Written Answer:**
> 1. **Which flow's guarantee the rejection protects:**
>    - **$f_4$'s own SLA guarantee:** Under the Parekh-Gallagher fair sharing formula, adding $f_4$ with weight $W_4 = 1$ results in a total weight $\Sigma W = 1 + 1 + 2 + 1 = 5$, granting $f_4$ a guaranteed rate of $(1/5) \times 10 = 2.0\text{ Mbps}$. Because $f_4$ requested $3.0\text{ Mbps}$, the network cannot fulfill its contract. Admitting it would break the guarantee promised to $f_4$.
>    - **The guarantees of active flows $f_1, f_2,$ and $f_3$:** The link capacity is $10\text{ Mbps}$, and the three active flows already requested $2 + 2 + 4 = 8\text{ Mbps}$, leaving only $2\text{ Mbps}$ of unallocated capacity. If the network forced $f_4$ to receive $3\text{ Mbps}$ by increasing its weight, the sum of requested rates ($11\text{ Mbps}$) would exceed the link's physical capacity ($10\text{ Mbps}$). This would dilute the bandwidth allocated to flows $f_1$, $f_2$, and $f_3$, causing their guaranteed rates to fall below their contractual rates ($2.0$, $2.0$, and $4.0\text{ Mbps}$). Hence, rejecting $f_4$ protects the integrity of the guarantees made to $f_1, f_2,$ and $f_3$.
>
> 2. **What weight or rate $f_4$ would need:**
>    - **Rate:** With its specified weight $W_4 = 1$, $f_4$ would be admitted if its requested rate is reduced to:
>      $$R_4 \le \mathbf{2.0\text{ Mbps}}$$
>    - **Weight:** No weight assignment can admit $f_4$ at $R_4 = 3.0\text{ Mbps}$ while preserving the guarantees of $f_1, f_2,$ and $f_3$, because the total demanded bandwidth ($11\text{ Mbps}$) exceeds link capacity $C = 10\text{ Mbps}$.

---

#### Part B: Traffic Policing
> **Question:** Explain why exactly two packets are dropped, in terms of the bucket capacity.
>
> **Written Answer:**
> The token bucket has a capacity of $b = 4$ tokens and starts completely full at $t = 0$. At time $t = 0$, an instantaneous burst of 6 packets arrives simultaneously ($\Delta t = 0$). Because no time has elapsed, zero new tokens are generated. Each packet requires $L = 1$ token. The first 4 packets consume the 4 tokens stored in the bucket, reducing the token count to 0. When the 5th and 6th packets arrive, zero tokens are available. Because traffic policing drops non-conforming packets immediately without buffering them, exactly $6 - b = 6 - 4 = \mathbf{2\text{ packets}}$ are dropped.

---

#### Part C: Traffic Shaping
> **Question:** Report the delay each packet experienced, and compare with Part B. State the single difference between shaping and policing that produces drops in one and delays in the other.
>
> **Written Answer:**
> 1. **Packet Delays in Shaping:**
>    - Packet 1 ($t_{\text{arr}} = 0$): Released at $t = 0$, Delay = $\mathbf{0.0}$
>    - Packet 2 ($t_{\text{arr}} = 0$): Released at $t = 0$, Delay = $\mathbf{0.0}$
>    - Packet 3 ($t_{\text{arr}} = 0$): Released at $t = 0$, Delay = $\mathbf{0.0}$
>    - Packet 4 ($t_{\text{arr}} = 0$): Released at $t = 0$, Delay = $\mathbf{0.0}$
>    - Packet 5 ($t_{\text{arr}} = 0$): Released at $t = 1$, Delay = $\mathbf{1.0}$
>    - Packet 6 ($t_{\text{arr}} = 0$): Released at $t = 2$, Delay = $\mathbf{2.0}$
>    - Packet 7 ($t_{\text{arr}} = 5$): Released at $t = 5$, Delay = $\mathbf{0.0}$
>    - Packet 8 ($t_{\text{arr}} = 6$): Released at $t = 6$, Delay = $\mathbf{0.0}$
>
> 2. **Comparison with Part B:**
>    In Part B (Policing), packets 5 and 6 were permanently dropped ($100\%$ loss). In Part C (Shaping), no packets were dropped ($0\%$ loss); instead, packets 5 and 6 experienced small delays of $1.0$ and $2.0$ time units until sufficient tokens accrued.
>
> 3. **The Single Fundamental Difference:**
>    The single difference is the presence of an internal **packet buffer (queue)**. Policing possesses no buffer, discarding non-conforming packets immediately upon arrival. Shaping maintains a buffer, delaying non-conforming packets until tokens accrue to emit a conforming, smoothed stream.

---

#### Part D: Packet Scheduling
> **Question:** Compare the two orders and explain how the weight-2 flow is served, and how weighted fair queuing protects a flow from being starved by another.
>
> **Written Answer:**
> 1. **Comparison of Orders:**
>    - WFQ Order:  $\mathbf{A \to C \to B \to E \to F \to G \to D \to H}$
>    - FIFO Order: $\mathbf{A \to B \to C \to D \to E \to F \to G \to H}$
>
> 2. **How the Weight-2 Flow (Flow 3) is Served:**
>    In WFQ, the virtual finish number increments by $\frac{\text{length}}{\text{weight}}$. Because Flow 3 has weight $w = 2$, its finish number slope is half as steep as Flow 1 and Flow 2 ($w = 1$). 
>    - When Packet C ($L=10$) arrives at $t=5$ alongside Packet B ($L=6$), Packet C's virtual transmission time is $10 / 2 = 5$, giving finish number $F_C = 10$, while B's is $6 / 1 = 6$, giving $F_B = 11$. Hence, C is transmitted before B.
>    - Similarly, Packet E ($F=14$) and Packet G ($F=19$) jump ahead of Flow 2's Packet D ($F=20$). Flow 3 receives exactly twice the bandwidth share of the link compared to the other flows.
>
> 3. **How WFQ Prevents Starvation:**
>    In FIFO, a misbehaving flow flooding packets will monopolize the queue and starve other flows. In WFQ, finish numbers are computed per-flow:
>    $$F_k = \max(\text{arrival}, F_{\text{prev}}) + \frac{L_k}{w_i}$$
>    If an aggressive flow sends a torrent of packets, its $F_{\text{prev}}$ accumulates far into the virtual future ($F \gg 100$). When a well-behaved flow transmits a packet, its finish number is calculated from its current arrival time, yielding a much lower finish number. The scheduler immediately preempts the backlog of the aggressive flow to serve the conforming flow. Thus, every active flow is mathematically guaranteed a minimum service rate of $\frac{w_i}{\sum w} \cdot C$, rendering starvation impossible.

---

## 10. Comprehensive Viva & Exam Preparation Guide

### Q1: What is Generalized Processor Sharing (GPS), and why can't it be implemented directly in hardware?
**Answer:** GPS is an idealized fluid-flow scheduling discipline where all active flows share the link simultaneously in continuous, infinitesimal quantities according to their weights. It cannot be implemented in packet-switched networks because packets are atomic, non-preemptible transmission units. A router must transmit one full packet at a time at link speed. WFQ was invented as a packet-by-packet discrete emulation of GPS.

### Q2: What does a packet's "Finish Number" represent in Weighted Fair Queuing?
**Answer:** The finish number $F$ is the timestamp at which the packet would have completed transmission under the idealized continuous GPS fluid model. Sorting and serving discrete packets by increasing order of finish number guarantees that packetized transmissions closely track the ideal GPS fairness bounds.

### Q3: What happens in WFQ if two packets have identical finish numbers?
**Answer:** If finish numbers are identical, a secondary tie-breaking rule is applied: typically earliest arrival time first (FIFO order among tied finish numbers), followed by deterministic flow ID ordering.

### Q4: Explain the difference between work-conserving and non-work-conserving schedulers.
**Answer:** 
- A **work-conserving scheduler** never leaves the transmission link idle if there is at least one packet waiting in the queue (e.g. WFQ, FIFO, Round Robin).
- A **non-work-conserving scheduler** may deliberately hold packets even if the link is idle, in order to enforce a precise delay bound or smooth egress traffic (e.g. Traffic Shapers, Stop-and-Go Queuing).

### Q5: Under what condition is Traffic Policing preferred over Traffic Shaping?
**Answer:** Traffic Policing is preferred at high-speed network boundaries and transit backbones (e.g. ISP ingress) where maintaining packet buffers for millions of flows is too memory-intensive and would introduce unacceptable latency and bufferbloat. Policing drops or marks out-of-profile packets instantly with $O(1)$ memory. Shaping is used at enterprise customer edges to prevent costly policing drops by the upstream ISP.

### Q6: Can a Token Bucket allow an infinite transmission burst?
**Answer:** No. The maximum instantaneous burst a token bucket can ever permit is strictly bounded by its bucket capacity $b$. If a burst arrives at peak line rate $C_{\text{in}} > r$, the maximum number of bytes transmitted during any time interval $\tau$ is bounded by:
$$\text{Data}(\tau) \le b + r \cdot \tau$$

### Q7: In the Parekh-Gallagher admission test, why do we divide by $\Sigma W$ rather than treating weights as absolute bandwidths?
**Answer:** Weights under GPS and WFQ are relative proportions, not absolute rates. Dividing by $\Sigma W$ normalizes the weights so that $100\%$ of link capacity $C$ is arbitrated:
$$\sum_{i} \left( \frac{W_i}{\sum_j W_j} \cdot C \right) = C$$
This ensures that if some flows terminate, the remaining active flows automatically share the freed bandwidth (work-conserving property) in proportion to their relative weights.

---
*End of Report · Prepared for CS353 Computer Networks*

