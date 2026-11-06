# CS353: Medium Access Control (Aloha vs. CSMA)
## Comprehensive Lab Report, Theory Guide & Implementation Manual
**Course:** CS353 · Computer Networks · Week 6 / Lab 6  
**Topic:** MAC Sublayer / Shared Channel Arbitration, Random Access Protocols, Throughput & Vulnerable Periods  
**Protocols Analyzed:** Pure Aloha, Slotted Aloha, and 1-Persistent CSMA in Python

---

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [Theoretical Foundations of Medium Access Control](#2-theoretical-foundations-of-medium-access-control)
   - [2.1 The Multi-Access Broadcast Channel Problem](#21-the-multi-access-broadcast-channel-problem)
   - [2.2 Offered Load ($G$) vs. Channel Throughput ($S$)](#22-offered-load-g-vs-channel-throughput-s)
   - [2.3 The Concept of the Vulnerable Window](#23-the-concept-of-the-vulnerable-window)
3. [Protocol Deep-Dive: Pure Aloha](#3-protocol-deep-dive-pure-aloha)
   - [3.1 Blind Transmission Strategy](#31-blind-transmission-strategy)
   - [3.2 Mathematical Derivation of $S = G e^{-2G}$](#32-mathematical-derivation-of-s--g-e-2g)
   - [3.3 Peak Throughput Limit ($18.4\%$)](#33-peak-throughput-limit-184)
4. [Protocol Deep-Dive: Slotted Aloha](#4-protocol-deep-dive-slotted-aloha)
   - [4.1 Discrete Time Slotting & Collision Halving](#41-discrete-time-slotting--collision-halving)
   - [4.2 Mathematical Derivation of $S = G e^{-G}$](#42-mathematical-derivation-of-s--g-e-g)
   - [4.3 Peak Throughput Limit ($36.8\%$)](#43-peak-throughput-limit-368)
5. [Protocol Deep-Dive: Carrier Sense Multiple Access (CSMA)](#5-protocol-deep-dive-carrier-sense-multiple-access-csma)
   - [5.1 "Listen Before Talk" Philosophy](#51-listen-before-talk-philosophy)
   - [5.2 1-Persistent, Non-Persistent, and p-Persistent Variants](#52-1-persistent-non-persistent-and-p-persistent-variants)
   - [5.3 Normalized Propagation Delay Parameter ($a$)](#53-normalized-propagation-delay-parameter-a)
6. [Comparative Simulation Benchmarks & Analysis (Part D)](#6-comparative-simulation-benchmarks--analysis-part-d)
   - [6.1 Throughput vs. Load Overlaid Curves](#61-throughput-vs-load-overlaid-curves)
   - [6.2 Why Aloha Collapses at High Load while CSMA Sustains](#62-why-aloha-collapses-at-high-load-while-csma-sustains)
   - [6.3 The Controlling Role of Propagation Delay ($a$)](#63-the-controlling-role-of-propagation-delay-a)
   - [6.4 Vulnerable Windows Linked to Peak Heights](#64-vulnerable-windows-linked-to-peak-heights)
7. [Software Architecture & Python Implementation (`assignment6.py`)](#7-software-architecture--python-implementation-assignment6py)
8. [Comprehensive Viva & Exam Preparation Guide](#8-comprehensive-viva--exam-preparation-guide)

---

## 1. Executive Summary

When multiple network stations share a single broadcast transmission medium (e.g., coaxial cable, shared radio spectrum, or satellite transponder), their transmissions can collide, corrupting data. The **Medium Access Control (MAC)** sublayer coordinates channel access among independent, uncoordinated stations.

In Lab 6, we implement Monte Carlo discrete-event simulations for the three foundational random-access MAC protocols:
1. **Pure Aloha:** Stations transmit immediately whenever data is ready. (Peak throughput $= \mathbf{18.4\%}$).
2. **Slotted Aloha:** Transmissions are synchronized to discrete time slots. (Peak throughput $= \mathbf{36.8\%}$).
3. **1-Persistent CSMA:** Stations sense the carrier before transmitting and defer when busy. (Peak throughput reaches $\mathbf{53\%}$ to $\mathbf{80\%}$ depending on propagation delay $a$).

```
+--------------------------------------------------------------------------------------------------+
|                                    MAC PROTOCOLS THROUGHPUT COMPARISON                           |
|                                                                                                  |
|   Throughput S                                                                                   |
|     ▲                                                                                            |
| 1.0 │                                                                                            |
|     │                                                                                            |
| 0.8 │                                                                                            |
|     │                                     1-Persistent CSMA (a = 0.01)                           |
| 0.6 │                                  .-----.                                                   |
|     │                                 /       \                                                  |
| 0.4 │                         Slotted Aloha    \                                                 |
|     │                         .-----.           \                                                |
| 0.2 │                 Pure Aloha     \           '----------------------------- (Sustained ~0.4) |
|     │                .----.           \                                                          |
| 0.0 └───┴───────────/──────┴───────────\─────────────────────────────► Offered Load G            |
|        0.0        0.5     1.0         2.0                           3.0                          |
+--------------------------------------------------------------------------------------------------+
```

---

## 2. Theoretical Foundations of Medium Access Control

### 2.1 The Multi-Access Broadcast Channel Problem
In traditional point-to-point links, two nodes possess a dedicated medium. In broadcast networks, all nodes share a single channel. If two nodes transmit simultaneously, their electromagnetic waveforms interfere destructively (a **collision**). The key design goals of a MAC protocol are:
- High channel utilization under high load.
- Low latency under light load.
- Decentralized coordination (no single point of failure).
- Fairness across competing stations.

### 2.2 Offered Load ($G$) vs. Channel Throughput ($S$)
1. **Throughput ($S$):** The rate of successfully delivered frames per frame transmission time ($T$). Since the channel can deliver at most one frame per time unit $T$, $0 \le S \le 1$.
2. **Offered Load ($G$):** The total rate of frame attempts generated per frame transmission time, including both **newly generated frames** and **retransmitted collided frames**.
   - Under light load ($G \ll 1$): Collisions are rare; $S \approx G$.
   - Under heavy load ($G > 1$): Retransmissions build up; collisions dominate.

### 2.3 The Concept of the Vulnerable Window
The **vulnerable window ($V$)** is the time interval during which the start of another frame transmission will collide with and destroy a target frame. The probability of zero collisions is governed by Poisson arrival statistics:

$$P(\text{Success}) = P(0 \text{ arrivals in window } V) = e^{-G \cdot (V / T)}$$

$$S = G \cdot P(\text{Success}) = G \cdot e^{-G \cdot (V / T)}$$

---

## 3. Protocol Deep-Dive: Pure Aloha

### 3.1 Blind Transmission Strategy
Invented at the University of Hawaii in 1970 by Norman Abramson, Pure Aloha operates on a completely uncoordinated principle:
> *"Whenever a station has a frame to send, it transmits immediately at full line rate."*

If a collision occurs, the station waits a random backoff time and retransmits.

### 3.2 Mathematical Derivation of $S = G e^{-2G}$
Let frame transmission time be $T = 1$. Suppose a station begins transmitting at time $t_0$:
- Any frame that started between $t_0 - 1$ and $t_0$ will collide with the beginning of the target frame.
- Any frame that starts between $t_0$ and $t_0 + 1$ will collide with the end of the target frame.

```
                  |<----------------- 2T ----------------->|
                  |                Vulnerable Period       |
------------------+--------------------+-------------------+------------------
             t0 - 1                   t0                  t0 + 1
                  |  [ Target Frame ]  |
```

The total vulnerable period is:
$$V_{\text{Pure Aloha}} = 2T = 2$$

Assuming Poisson frame generation with rate $G$, the probability that zero frames arrive during interval $2T$ is $e^{-2G}$. Therefore, throughput is:

$$S_{\text{Pure Aloha}} = G \cdot e^{-2G}$$

### 3.3 Peak Throughput Limit ($18.4\%$)
To find the maximum achievable throughput, we differentiate $S$ with respect to $G$ and set to zero:

$$\frac{dS}{dG} = e^{-2G} + G(-2)e^{-2G} = e^{-2G}(1 - 2G) = 0 \implies G = \frac{1}{2} = \mathbf{0.5}$$

Substituting $G = 0.5$:
$$S_{\max} = 0.5 \cdot e^{-2(0.5)} = \frac{0.5}{e} = \frac{1}{2e} \approx \mathbf{0.1839} \approx \mathbf{18.4\%}$$

Pure Aloha wastes over **$81.6\%$ of channel capacity** in collisions at peak load!

---

## 4. Protocol Deep-Dive: Slotted Aloha

### 4.1 Discrete Time Slotting & Collision Halving
In 1972, Lawrence Roberts proposed **Slotted Aloha**:
- Time is partitioned into discrete intervals (slots) of duration equal to frame transmission time $T$.
- A station cannot transmit immediately; it must wait until the boundary of the next time slot.

```
Slot 1              Slot 2              Slot 3
[─────── T ───────] [─────── T ───────] [─────── T ───────]
Frame A ───► Collision! (Both transmit in Slot 1)
Frame B ───►
                    Frame C ───► Success! (Sole transmission in Slot 2)
```

Because transmissions are synchronized to slot boundaries, frames either overlap completely or not at all. Partial overlaps are completely eliminated!

### 4.2 Mathematical Derivation of $S = G e^{-G}$
The vulnerable period for a given slot is simply the duration of that single slot:
$$V_{\text{Slotted Aloha}} = 1T = 1$$

The probability of zero other arrivals during the slot is $e^{-G}$. Thus:

$$S_{\text{Slotted Aloha}} = G \cdot e^{-G}$$

### 4.3 Peak Throughput Limit ($36.8\%$)
Differentiating and solving for the maximum:
$$\frac{dS}{dG} = e^{-G} - G e^{-G} = e^{-G}(1 - G) = 0 \implies G = \mathbf{1.0}$$

Substituting $G = 1.0$:
$$S_{\max} = 1.0 \cdot e^{-1.0} = \frac{1}{e} \approx \mathbf{0.3678} \approx \mathbf{36.8\%}$$

> **Key Result:** Synchronizing transmissions into discrete time slots exactly **halves the vulnerable window** from $2T$ to $1T$, which exactly **doubles the channel capacity** from $18.4\%$ to $36.8\%$.

---

## 5. Protocol Deep-Dive: Carrier Sense Multiple Access (CSMA)

### 5.1 "Listen Before Talk" Philosophy
Aloha stations transmit blindly without checking channel state. In **Carrier Sense Multiple Access (CSMA)**, a station listens to the physical channel before attempting to transmit:
- **If channel is busy:** Defer transmission to avoid a guaranteed collision.
- **If channel is idle:** Transmit according to persistence rules.

### 5.2 1-Persistent, Non-Persistent, and p-Persistent Variants
1. **1-Persistent CSMA:** If idle, transmit immediately with probability $p=1$. If busy, continue listening continuously until idle, then transmit immediately. (Used in standard 802.3 Ethernet).
2. **Non-Persistent CSMA:** If idle, transmit. If busy, do not keep listening; wait a random backoff period before sensing again. (Reduces collisions at high load, but increases idle time).
3. **p-Persistent CSMA (Slotted):** If idle, transmit with probability $p$; defer to the next slot with probability $1-p$. (Used in 802.11 Wi-Fi DCF).

### 5.3 Normalized Propagation Delay Parameter ($a$)
Why do collisions still occur in CSMA if stations listen before talking?
> **Root Cause:** **Propagation Delay!** Electromagnetic signals travel at the speed of light ($c \approx 2 \times 10^8\text{ m/s}$ in copper). If Station A starts transmitting at $t = 0$, Station B (located across the cable) will sense the channel as idle until the wavefront arrives at time $t = \tau = T_{\text{prop}}$. If Station B transmits during this delay window, a collision occurs!

The dimensionless ratio governing CSMA efficiency is:
$$a = \frac{T_{\text{prop}}}{T_{\text{trans}}}$$

The vulnerable window of 1-persistent CSMA is strictly equal to the propagation delay $a$. When $a \to 0$, the vulnerable window shrinks to zero, and throughput approaches $100\%$.

---

## 6. Comparative Simulation Benchmarks & Analysis (Part D)

### 6.1 Throughput vs. Load Overlaid Curves
The Monte Carlo simulation in `assignment6.py` produces the canonical comparative curves saved in `comparison.png`:

| Protocol | Vulnerable Period ($V$) | Peak Throughput ($S_{\max}$) | Optimal Load ($G^*$) | High-Load Behavior ($G \to 3.0$) |
| :--- | :---: | :---: | :---: | :--- |
| **Pure Aloha** | $2.0$ | $\mathbf{0.184}$ | $0.5$ | Collapses toward **0.00** |
| **Slotted Aloha**| $1.0$ | $\mathbf{0.368}$ | $1.0$ | Collapses toward **0.00** |
| **1-Persistent CSMA ($a=0.01$)** | $\mathbf{0.01}$ | $\mathbf{0.527}$ | $0.90$ | Sustains high throughput ($\approx \mathbf{0.40}$) |

---

### 6.2 Why Aloha Collapses at High Load while CSMA Sustains

#### 1. Aloha Collapse:
In Pure and Slotted Aloha, stations transmit blindly without sensing the channel. As offered load $G$ increases, the probability of two or more frames overlapping increases exponentially ($1 - e^{-2G}$). Because transmissions are uncoordinated, high load causes virtually every single frame to collide. The channel becomes saturated with overlapping corrupted frames, and throughput collapses to zero (the channel "jams" itself).

#### 2. CSMA Sustained Performance:
In 1-persistent CSMA, stations listen before talking. If Station A is transmitting, all other stations detect the carrier and **defer their transmissions**. This serializes the traffic. Even when $G$ is very high, collisions only occur if two stations transmit during the minute vulnerable window $a$. Thus, CSMA prevents chaotic overlaps and maintains high throughput even under severe load.

---

### 6.3 The Controlling Role of Propagation Delay ($a$)
The simulation varies $a$ across $0.01$, $0.05$, and $0.10$ (`csma_varying_a.png`):
- **$a = 0.01$:** Peak $S \approx \mathbf{0.527}$ at $G = 0.90$
- **$a = 0.05$:** Peak $S \approx \mathbf{0.497}$ at $G = 1.00$
- **$a = 0.10$:** Peak $S \approx \mathbf{0.452}$ at $G = 0.90$

As $a$ increases, it takes longer for a station's signal to propagate across the medium. The vulnerable window expands, increasing the probability that another station will falsely sense the channel as idle and transmit, driving down peak throughput.

---

### 6.4 Vulnerable Windows Linked to Peak Heights
The maximum achievable throughput of each protocol is directly governed by the physical duration of its vulnerable window:
1. **Pure Aloha ($V = 2.0$):** Largest vulnerable window $\implies$ maximum collision probability $\implies$ lowest peak ($\approx 18\%$).
2. **Slotted Aloha ($V = 1.0$):** Slotting halves the window $\implies$ collision probability reduced $\implies$ peak exactly doubles ($\approx 37\%$).
3. **1-Persistent CSMA ($V = a = 0.01$):** Carrier sensing shrinks the vulnerable window by a factor of 100 $\implies$ collisions are drastically curtailed $\implies$ peak climbs above $53\%$.

---

## 7. Software Architecture & Python Implementation (`assignment6.py`)

The simulation script models:
- `simulate_pure_aloha(G)`: Poisson arrival process; checks left/right inter-arrival gaps $> 1$.
- `simulate_slotted_aloha(G)`: Evaluates Poisson arrivals per slot ($P(k=1)$).
- `simulate_csma(G, a)`: Implements carrier sensing, tracking busy time $T_{\text{busy}} = t_{\text{transmit}} + 1 + a$ and deferred packet queues.
- Generates publication-quality plots: `comparison.png`, `pure_aloha.png`, `slotted_aloha.png`, and `csma_varying_a.png`.

---

## 8. Comprehensive Viva & Exam Preparation Guide

### Q1: Why is the vulnerable period of Pure Aloha equal to $2T$?
**Answer:** A frame of length $T$ that starts transmission at time $t_0$ can collide with any frame starting between $t_0 - T$ and $t_0$ (which overlaps with its beginning), or any frame starting between $t_0$ and $t_0 + T$ (which overlaps with its ending). The union of these two intervals is $(t_0 - T, t_0 + T)$, which has a total duration of $2T$.

### Q2: What is the primary operational requirement of Slotted Aloha compared to Pure Aloha?
**Answer:** Slotted Aloha requires **global clock synchronization**. Every station must share a common time reference (e.g. GPS or master beacon) so that all transmissions begin precisely at slot boundaries. Pure Aloha requires zero synchronization.

### Q3: Why does CSMA perform poorly over satellite links?
**Answer:** Geostationary satellite links have large propagation delays ($\text{RTT} \approx 500\text{ ms}$). This makes the normalized propagation delay parameter $a = T_{\text{prop}} / T_{\text{trans}}$ extremely large ($a \gg 1$). A station listening to the channel cannot know if an earth station on the other side of the planet started transmitting 200 ms ago, making carrier sensing virtually useless.

### Q4: What is the difference between 1-persistent and non-persistent CSMA?
**Answer:** 
- In **1-persistent CSMA**, when a station senses the channel as busy, it waits continuously until the channel becomes idle and immediately transmits. If multiple stations were waiting, they will all transmit simultaneously, causing a guaranteed collision.
- In **non-persistent CSMA**, when a station senses the channel as busy, it does not keep listening; it backs off for a random time interval before checking again. This staggers deferred transmissions and avoids mass collisions, but introduces channel idle time under light loads.

### Q5: What is CSMA/CD, and how does it improve upon basic CSMA?
**Answer:** CSMA with Collision Detection (CSMA/CD, IEEE 802.3 Ethernet) adds hardware circuitry that allows a station to **listen while transmitting**. If a collision is detected mid-transmission, the station immediately aborts transmitting, sends a 48-bit jam signal, and enters exponential backoff. This prevents wasting channel time transmitting the remainder of an already corrupted frame.

---
*End of Lab 6 Report · Prepared for CS353 Computer Networks*

