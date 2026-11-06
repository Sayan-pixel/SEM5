# CS353: Sliding-Window ARQ (Go-Back-N & Selective Repeat)
## Comprehensive Lab Report, Theory Guide & Implementation Manual
**Course:** CS353 · Computer Networks · Week 5 / Lab 5  
**Topic:** Data Link Layer / Reliable Byte-Stream Delivery, Flow Control & Sliding-Window ARQ Protocols  
**Protocols Analyzed:** Stop-and-Wait, Go-Back-N (GBN), and Selective Repeat (SR) in Python

---

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [Theoretical Foundations of Reliable Data Transfer](#2-theoretical-foundations-of-reliable-data-transfer)
   - [2.1 Stop-and-Wait Efficiency & The Bandwidth-Delay Product (BDP)](#21-stop-and-wait-efficiency--the-bandwidth-delay-product-bdp)
   - [2.2 Pipelining and Sliding Windows](#22-pipelining-and-sliding-windows)
   - [2.3 Go-Back-N vs. Selective Repeat Architecture](#23-go-back-n-vs-selective-repeat-architecture)
3. [Protocol Deep-Dive: Go-Back-N (GBN)](#3-protocol-deep-dive-go-back-n-gbn)
   - [3.1 Sender Window State & Cumulative ACKs](#31-sender-window-state--cumulative-acks)
   - [3.2 The Strict Receive-Window-Size-1 Invariant](#32-the-strict-receive-window-size-1-invariant)
   - [3.3 Timeout Behavior & Mass Window Retransmission](#33-timeout-behavior--mass-window-retransmission)
4. [Protocol Deep-Dive: Selective Repeat (SR)](#4-protocol-deep-dive-selective-repeat-sr)
   - [4.1 Dual Sender/Receiver Sliding Windows](#41-dual-senderreceiver-sliding-windows)
   - [4.2 Individual ACKs & Out-of-Order Buffering](#42-individual-acks--out-of-order-buffering)
   - [4.3 Targeted Retransmissions & Zero Frame Waste](#43-targeted-retransmissions--zero-frame-waste)
5. [Experimental Scenarios & Simulation Benchmarks](#5-experimental-scenarios--simulation-benchmarks)
   - [5.1 Scenario S1 ($W=4$, Drop Frame 2) Trace & Analysis](#51-scenario-s1-w4-drop-frame-2-trace--analysis)
   - [5.2 Scenario S2 ($W=8$, Drop Frame 0) Trace & Analysis](#52-scenario-s2-w8-drop-frame-0-trace--analysis)
   - [5.3 Retransmission Overhead & Efficiency Widening](#53-retransmission-overhead--efficiency-widening)
6. [The Fundamental Sequence-Number Space Theorems](#6-the-fundamental-sequence-number-space-theorems)
   - [6.1 Proof of the $W + 1$ Bound for Go-Back-N](#61-proof-of-the-w--1-bound-for-go-back-n)
   - [6.2 Proof of the $2W$ Bound for Selective Repeat](#62-proof-of-the-2w-bound-for-selective-repeat)
7. [Software Architecture & Python Implementation (`assignment5.py`)](#7-software-architecture--python-implementation-assignment5py)
8. [Comprehensive Viva & Exam Preparation Guide](#8-comprehensive-viva--exam-preparation-guide)

---

## 1. Executive Summary

When packets cross noisy channels, frames and acknowledgments (ACKs) can be dropped or corrupted. To provide reliable, in-order delivery to upper layers without stalling high-speed physical links, the Data Link and Transport layers deploy **Sliding-Window Automatic Repeat reQuest (ARQ)** protocols.

In Lab 5, we simulate, analyze, and compare the two canonical sliding-window protocols:
1. **Go-Back-N (GBN):** Uses a sender window of size $W$, cumulative ACKs, and a receive window of size $1$. When a frame drops, all subsequent safely delivered frames in the window are discarded by the receiver, forcing the sender to "go back" and retransmit the entire outstanding window.
2. **Selective Repeat (SR):** Uses matching sender and receiver windows of size $W$, individual ACKs, and receiver-side buffering. Only the specifically dropped frame is retransmitted, preserving all safely arrived out-of-order frames.

```
+--------------------------------------------------------------------------------------------------+
|                                    GBN VS. SELECTIVE REPEAT LOSS BEHAVIOR                        |
|                                                                                                  |
| 1. GO-BACK-N (W = 4, Frame 2 Dropped):                                                           |
|    Send: [0] ──► Delivered (ACK 0)                                                               |
|    Send: [1] ──► Delivered (ACK 1)                                                               |
|    Send: [2] ──X DROPPED!                                                                        |
|    Send: [3] ──► Arrives, but DISCARDED! (Receiver only wants 2)                                 |
|    TIMEOUT on 2 ──► Sender must RESEND BOTH [2] and [3]!                                         |
|                                                                                                  |
| 2. SELECTIVE REPEAT (W = 4, Frame 2 Dropped):                                                    |
|    Send: [0] ──► Delivered (ACK 0)                                                               |
|    Send: [1] ──► Delivered (ACK 1)                                                               |
|    Send: [2] ──X DROPPED!                                                                        |
|    Send: [3] ──► Arrives, BUFFERED in receive window! (ACK 3 sent)                               |
|    TIMEOUT on 2 ──► Sender ONLY RESENDS [2]!                                                     |
|    [2] Delivered ──► Receiver delivers [2, 3] to upper layer in order!                           |
+--------------------------------------------------------------------------------------------------+
```

---

## 2. Theoretical Foundations of Reliable Data Transfer

### 2.1 Stop-and-Wait Efficiency & The Bandwidth-Delay Product (BDP)
In a primitive **Stop-and-Wait** protocol, the transmitter sends one frame and pauses until it receives an ACK. Over long distances (e.g., cross-country fibre or satellite), link utilization collapses:

$$U_{\text{Stop-and-Wait}} = \frac{T_{\text{trans}}}{T_{\text{trans}} + 2 \cdot T_{\text{prop}}} = \frac{1}{1 + 2a}, \quad \text{where } a = \frac{T_{\text{prop}}}{T_{\text{trans}}}$$

For high-speed links where propagation delay $T_{\text{prop}}$ dwarfs transmission time $T_{\text{trans}}$ ($a \gg 1$), utilization drops below $1\%$. The link sits idle for $99\%$ of the round-trip time.

### 2.2 Pipelining and Sliding Windows
To saturate the link's **Bandwidth-Delay Product ($\text{BDP} = \text{Bandwidth} \times \text{RTT}$)**, protocols use **pipelining**: the sender transmits up to $W$ unacknowledged frames before pausing. The maximum theoretical link utilization becomes:

$$U = \min\left(1, \frac{W}{1 + 2a}\right)$$

Selecting window size $W \ge 1 + 2a$ allows the sender to achieve **$100\%$ link utilization**.

### 2.3 Go-Back-N vs. Selective Repeat Architecture

| Metric / Feature | Go-Back-N (GBN) | Selective Repeat (SR) |
| :--- | :--- | :--- |
| **Sender Window Size ($W_s$)** | $W > 1$ | $W > 1$ |
| **Receiver Window Size ($W_r$)**| **$1$ (Strictly in-order)** | **$W$ (Buffers out-of-order)** |
| **Acknowledgment Type** | Cumulative (`ACK n` confirms all $\le n$) | Individual (`ACK n` confirms only $n$) |
| **Receiver Memory Buffer** | None (discards out-of-order frames) | Requires $W$-frame reorder buffer |
| **Sender Timers** | Single timer for oldest unacked frame | Independent timer per unacked frame |
| **Retransmissions on Loss** | Up to $W$ frames (cascading retransmits) | Exactly $1$ frame (target retransmit) |
| **Min Sequence Space ($N_{\min}$)**| **$W + 1$** | **$2W$** |

---

## 3. Protocol Deep-Dive: Go-Back-N (GBN)

### 3.1 Sender Window State & Cumulative ACKs
The sender maintains three pointers:
- `base`: Sequence number of the oldest unacknowledged frame.
- `nextseqnum`: Sequence number of the next frame to be transmitted.
- $W$: Maximum allowable outstanding frames ($nextseqnum < base + W$).

An `ACK n` is **cumulative**: it informs the sender that all frames up to and including sequence number $n$ have been received successfully. When `ACK n` arrives, `base` advances to $n + 1$.

### 3.2 The Strict Receive-Window-Size-1 Invariant
The GBN receiver maintains a single variable: `expectedseqnum`.
- If a frame arrives with sequence number equal to `expectedseqnum`: it delivers the payload to the network layer, increments `expectedseqnum`, and transmits an ACK.
- If a frame arrives with sequence number $\ne expectedseqnum$ (even if safely intact): **it is unconditionally discarded**.

### 3.3 Timeout Behavior & Mass Window Retransmission
The sender runs a single timer associated with `base`. If an ACK is not received before the timer expires:
$$\text{Action on Timeout:} \quad \text{Retransmit all frames from } \text{base} \text{ up to } (\text{nextseqnum} - 1)$$
Even if frames $base + 1, base + 2, \dots$ arrived intact at the receiver, they were thrown away. The sender must retransmit every one of them.

---

## 4. Protocol Deep-Dive: Selective Repeat (SR)

### 4.1 Dual Sender/Receiver Sliding Windows
Selective Repeat maintains sliding windows of size $W$ at **both** endpoints:
- Sender Window: Tracks unacknowledged frames and maintains an independent timer for each transmitted packet.
- Receiver Window: Maintains a buffer of size $W$ centered at `rcv_base`.

### 4.2 Individual ACKs & Out-of-Order Buffering
When frame $k$ arrives at the receiver:
- If $k \in [rcv\_base, rcv\_base + W - 1]$: It generates an individual `ACK k`.
- If $k = rcv\_base$: It delivers frame $k$ and any consecutively buffered frames ($k+1, k+2, \dots$) to the application, sliding `rcv_base` forward!
- If $k > rcv\_base$: It places frame $k$ into its buffer to await the missing predecessors.

### 4.3 Targeted Retransmissions & Zero Frame Waste
When a timer expires for packet $k$, **only packet $k$ is retransmitted**. The sender never retransmits frames that have already been acknowledged, completely eliminating redundant transmissions.

---

## 5. Experimental Scenarios & Simulation Benchmarks

### 5.1 Scenario S1 ($W=4$, Drop Frame 2) Trace & Analysis
- **Parameters:** 6 payloads ($0, 1, 2, 3, 4, 5$), Window size $W = 4$.
- **Injected Error:** Data frame 2 is dropped during round 1.

#### Trace Results:
- **Go-Back-N Execution:**
  - Round 1: Sender sends $0, 1, 2, 3$. Frame 2 drops. Frame 3 arrives at receiver but is discarded.
  - Round 2: Timeout on 2. Sender goes back and resends **both Frame 2 and Frame 3**. Frames $2, 3, 4, 5$ transmitted.
  - Total Transmissions: $\mathbf{8}$ (Payloads: 6, Resent: `2, 3`).
- **Selective Repeat Execution:**
  - Round 1: Sender sends $0, 1, 2, 3$. Frame 2 drops. Frame 3 arrives and is buffered by receiver (`ACK 3` sent).
  - Round 2: Timeout on 2. Sender retransmits **only Frame 2**.
  - Total Transmissions: $\mathbf{7}$ (Payloads: 6, Resent: `2`).

---

### 5.2 Scenario S2 ($W=8$, Drop Frame 0) Trace & Analysis
- **Parameters:** 8 payloads ($0 \text{ to } 7$), Window size $W = 8$.
- **Injected Error:** Data frame 0 is dropped during round 1.

#### Trace Results:
- **Go-Back-N Execution:**
  - Round 1: Sender sends all 8 frames ($0, 1, 2, 3, 4, 5, 6, 7$). Frame 0 drops. Frames 1–7 arrive at receiver but are **all discarded**!
  - Round 2: Timeout on 0. Sender must retransmit **all 8 frames** ($0, 1, 2, 3, 4, 5, 6, 7$).
  - Total Transmissions: $\mathbf{16}$ (Payloads: 8, Resent: `0, 1, 2, 3, 4, 5, 6, 7`).
- **Selective Repeat Execution:**
  - Round 1: Sender sends frames 0–7. Frame 0 drops. Frames 1–7 arrive and are buffered.
  - Round 2: Timeout on 0. Sender retransmits **only Frame 0**. Receiver receives 0 and releases all 8 frames in order.
  - Total Transmissions: $\mathbf{9}$ (Payloads: 8, Resent: `0`).

---

### 5.3 Retransmission Overhead & Efficiency Widening

$$\text{Retransmission Overhead} = \frac{\text{Total Frame Transmissions}}{\text{Number of Unique Payloads}}$$

| Scenario | Window Size ($W$) | Dropped Frame | GBN Overhead | SR Overhead | Overhead Gap ($\Delta$) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **S1** | 4 | Frame 2 | $8 / 6 \approx \mathbf{1.33}$ | $7 / 6 \approx \mathbf{1.17}$ | $0.16$ |
| **S2** | 8 | Frame 0 | $16 / 8 = \mathbf{2.00}$ | $9 / 8 = \mathbf{1.125}$ | $\mathbf{0.875}$ |

#### Key Analytical Conclusions:
1. **Window Scaling Effect:** As window size $W$ expands, the efficiency gap between GBN and SR **widens dramatically**. In GBN, a single loss can trigger up to $W$ retransmissions, whereas SR always retransmits exactly 1 frame per loss.
2. **Channel Cleanliness Effect:** As packet loss rate approaches zero, the overhead for both protocols converges to $1.00$ ($N/N$). Over clean links (e.g. high-speed LANs), GBN is often preferred for its lower implementation complexity and minimal memory footprint.

---

## 6. The Fundamental Sequence-Number Space Theorems

Because sequence numbers are carried in fixed-size header fields of $k$ bits, the sequence space wraps around modulo $2^k$. If the sequence space is too small relative to window size $W$, the receiver cannot distinguish between a **retransmitted old frame** and a **brand-new frame**!

### 6.1 Proof of the $W + 1$ Bound for Go-Back-N
> **Theorem:** For Go-Back-N with window size $W$, the sequence number space must satisfy $N \ge W + 1$.

#### Proof by Contradiction:
Suppose $N = W$, using sequence numbers $\{0, 1, \dots, W-1\}$.
1. The sender transmits frames $0, 1, \dots, W-1$.
2. The receiver receives all $W$ frames successfully, delivers them, advances its `expectedseqnum` to $W \pmod W = 0$, and sends a cumulative ACK for $W-1$.
3. **Catastrophe:** The ACK is completely lost in transit.
4. The sender times out and retransmits the **old frame 0**.
5. The receiver is currently expecting sequence number **0** (which it expects to be the *new* packet from the next window).
6. The receiver accepts the old duplicate frame 0 as fresh data! Data corruption occurs.

If $N = W + 1$:
- The receiver advances its expectation to $W$.
- When the retransmitted old frame 0 arrives, the receiver sees $0 \ne W$, immediately detects it as an out-of-order duplicate, and discards it! Thus, **$N \ge W + 1$ is necessary and sufficient**.

---

### 6.2 Proof of the $2W$ Bound for Selective Repeat
> **Theorem:** For Selective Repeat with window size $W$, the sequence number space must satisfy $N \ge 2W$.

#### Proof by Construction & Edge Case:
Let sender and receiver window sizes be $W$.
1. **Initial State:** Sender window $= [0, W-1]$. Receiver window $= [0, W-1]$.
2. The sender transmits all $W$ frames ($0 \text{ to } W-1$).
3. The receiver successfully receives all $W$ frames, buffers them, sends individual ACKs for each ($ACK_0, \dots, ACK_{W-1}$), and advances its receive window completely forward to:
   $$\text{Receiver Window} = [W, 2W-1]$$
4. **Worst-Case Loss:** All $W$ ACKs are dropped by the channel.
5. The sender times out on frame 0 and retransmits **old frame 0**.
6. If the sequence number space $N < 2W$ (e.g. $N = 2W - 1$), the advanced receiver window $[W, 2W-1]$ wraps around such that sequence number $0$ falls inside the receiver's active window!
7. The receiver would accept the retransmitted old frame 0 as brand-new data belonging to the subsequent window, causing silent undetected data corruption.
8. To ensure the receiver window $[W, 2W-1]$ never overlaps with the sender's current unacknowledged window $[0, W-1]$, the total sequence space must be at least:
   $$N \ge W + W = \mathbf{2W}$$

---

## 7. Software Architecture & Python Implementation (`assignment5.py`)

The script `assignment5.py` models discrete communication rounds:
- `run_gbn(payloads, W, drops, verbose)`:
  - Models cumulative ACKs.
  - Implements strict ordered delivery (`expectedseqnum`).
  - Simulates 1-round timeout causing window retransmissions.
- `run_sr(payloads, W, drops, verbose)`:
  - Models individual ACKs.
  - Implements receiver buffer mapping sequence numbers to payloads.
  - Manages sliding receiver window advancement.

---

## 8. Comprehensive Viva & Exam Preparation Guide

### Q1: Why does Go-Back-N discard correctly received frames that arrive out of order?
**Answer:** The GBN receiver operates with a receive window of size 1 and has no buffer memory to store out-of-order frames. It is architected around cumulative acknowledgments. Because it can only acknowledge contiguous in-order frames, retaining an out-of-order frame would provide no benefit—the sender would still time out and retransmit it anyway.

### Q2: What is the condition under which Go-Back-N and Selective Repeat behave identically with zero wasted transmissions?
**Answer:** They behave identically when either:
1. The channel is perfectly reliable with zero frame or ACK drops ($P_{\text{loss}} = 0$).
2. The window size is set to $W = 1$ (which reduces both protocols to Stop-and-Wait ARQ).

### Q3: Why does Selective Repeat require twice the sequence number space ($2W$) compared to its window size $W$?
**Answer:** In Selective Repeat, the receiver's window can slide forward by up to $W$ positions while the sender's window remains static (if all ACKs from the first window are lost in transit). To ensure that retransmitted frames from the sender's old window do not overlap with the new sequence numbers of the receiver's advanced window, the sequence space must be at least $W + W = 2W$.

### Q4: What is the Bandwidth-Delay Product (BDP), and how does it dictate the minimum sliding window size?
**Answer:** The Bandwidth-Delay Product ($\text{BDP} = \text{Capacity} \times \text{RTT}$) represents the maximum volume of data that can be in-flight in the transmission pipe at any given moment. To keep the pipe full and achieve $100\%$ link utilization, the sliding window size $W$ must be at least equal to the BDP expressed in units of frame size:
$$W \ge 1 + \frac{2 \cdot T_{\text{prop}}}{T_{\text{trans}}}$$

### Q5: What are the implementation trade-offs between GBN and SR in hardware/operating systems?
**Answer:**
- **GBN Trade-offs:** Simple to implement; requires minimal RAM (no receiver buffer); sender needs only one timer. However, it wastes significant bandwidth over high-delay, lossy links.
- **SR Trade-offs:** Maximizes link efficiency by avoiding redundant transmissions. However, it requires complex receiver buffering, packet reassembly logic, and multiple independent timers at the sender.

---
*End of Lab 5 Report · Prepared for CS353 Computer Networks*

