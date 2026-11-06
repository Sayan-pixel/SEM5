# CS353: Reading the IPv4 Header with Wireshark
## Comprehensive Lab Report, Theory Guide & Implementation Manual
**Course:** CS353 · Computer Networks · Week 9 / Lab 9  
**Topic:** Network Layer / IPv4 Protocol Architecture, One's-Complement Checksum & Datagram Fragmentation  
**System Implemented:** 16-Bit Internet Checksum Verifier and IP Fragment Reassembler in Python (`checksumVerify.py`)

---

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [Theoretical Foundations of the IPv4 Header](#2-theoretical-foundations-of-the-ipv4-header)
   - [2.1 The IPv4 Datagram Architecture (RFC 791)](#21-the-ipv4-datagram-architecture-rfc-791)
   - [2.2 Detailed Bitfield Breakdown of all 14 Fields](#22-detailed-bitfield-breakdown-of-all-14-fields)
   - [2.3 Maximum Transmission Unit (MTU) & The Need for Fragmentation](#23-maximum-transmission-unit-mtu--the-need-for-fragmentation)
3. [The 16-Bit Internet Header Checksum Algorithm](#3-the-16-bit-internet-header-checksum-algorithm)
   - [3.1 One's-Complement Arithmetic & End-Around Carry Folding](#31-ones-complement-arithmetic--end-around-carry-folding)
   - [3.2 Verification Property: Why a Valid Header Folds to `0xFFFF`](#32-verification-property-why-a-valid-header-folds-to-0xffff)
   - [3.3 Incremental Checksum Updating (RFC 1624)](#33-incremental-checksum-updating-rfc-1624)
4. [Part A: Wireshark Header Analysis & Field Reconstruction](#4-part-a-wireshark-header-analysis--field-reconstruction)
   - [4.1 Dissection of Clean Packet 1](#41-dissection-of-clean-packet-1)
   - [4.2 Cross-Reconciliation Table](#42-cross-reconciliation-table)
5. [Part B: Mathematical Checksum Verification & TTL Corruption](#5-part-b-mathematical-checksum-verification--ttl-corruption)
   - [5.1 Manual 16-Bit Word Addition of Clean Header](#51-manual-16-bit-word-addition-of-clean-header)
   - [5.2 Simulating Router TTL Decrement & Checksum Invalidation](#52-simulating-router-ttl-decrement--checksum-invalidation)
   - [5.3 Wireshark Checksum Validation Setting](#53-wireshark-checksum-validation-setting)
6. [Part C: IP Datagram Fragmentation & Reassembly](#6-part-c-ip-datagram-fragmentation--reassembly)
   - [6.1 The Identification, Flags (DF, MF) and Fragment Offset Triple](#61-the-identification-flags-df-mf-and-fragment-offset-triple)
   - [6.2 Reassembly Algorithm & Math Trace of Fragments 3, 4, and 5](#62-reassembly-algorithm--math-trace-of-fragments-3-4-and-5)
   - [6.3 Verification of Reassembled 3000-Byte Payload](#63-verification-of-reassembled-3000-byte-payload)
7. [Part D: Deep-Dive Analysis (Answering Lab Questions)](#7-part-d-deep-dive-analysis-answering-lab-questions)
   - [7.1 Why TTL Forces Checksum Recomputation at Every Hop](#71-why-ttl-forces-checksum-recomputation-at-every-hop)
   - [7.2 The 8-Byte Boundary Rule: Why Fragment Offset Units are 8 Bytes](#72-the-8-byte-boundary-rule-why-fragment-offset-units-are-8-bytes)
   - [7.3 Why the Checksum Covers Only the Header (and Why IPv6 Dropped It)](#73-why-the-checksum-covers-only-the-header-and-why-ipv6-dropped-it)
8. [Software Architecture & Python Implementation (`checksumVerify.py`)](#8-software-architecture--python-implementation-checksumverifypy)
9. [Comprehensive Viva & Exam Preparation Guide](#9-comprehensive-viva--exam-preparation-guide)

---

## 1. Executive Summary

The Internet Protocol version 4 (IPv4, defined in IETF RFC 791) provides host-to-host best-effort connectionless datagram delivery across the Internet. To ensure correct routing and multiplexing, every IPv4 packet carries a 20-to-60 byte structured header.

In Lab 9, we inspect real-world captured packet traces (`lab9_ipv4.pcap`) using Wireshark and write algorithmic verification scripts in Python to uncover two core mathematical mechanisms that Wireshark calculates behind the scenes:
1. **The 16-Bit One's-Complement Checksum:** Mathematically validating header integrity and demonstrating how decremented Time-to-Live (TTL) corrupts a stale checksum.
2. **IP Datagram Fragmentation & Reassembly:** Slicing a large 3000-byte datagram into three discrete MTU-compliant fragments and reassembling them using 8-byte scaled offset arithmetic.

```
+--------------------------------------------------------------------------------------------------+
|                                    IPv4 HEADER ARCHITECTURE (RFC 791)                            |
|                                                                                                  |
|  0                   1                   2                   3                                   |
|  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1                                 |
| +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+                                |
| |Version|  IHL  |Type of Service|          Total Length         |  Byte 0 - 3                    |
| +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+                                |
| |         Identification        |Flags|      Fragment Offset    |  Byte 4 - 7                    |
| +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+                                |
| |  Time to Live |    Protocol   |        Header Checksum        |  Byte 8 - 11                   |
| +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+                                |
| |                       Source IP Address                       |  Byte 12 - 15                  |
| +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+                                |
| |                    Destination IP Address                     |  Byte 16 - 19                  |
| +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+                                |
| |                    Options (if IHL > 5) ...                   |  Byte 20 - ...                 |
| +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+                                |
+--------------------------------------------------------------------------------------------------+
```

---

## 2. Theoretical Foundations of the IPv4 Header

### 2.1 The IPv4 Datagram Architecture (RFC 791)
An IPv4 datagram consists of a variable-length header followed by payload data. The minimum header length without options is **$20\text{ bytes}$** (five 32-bit words).

### 2.2 Detailed Bitfield Breakdown of all 14 Fields
1. **Version (4 bits):** IP protocol version. Always `4` (`0100` binary).
2. **Internet Header Length (IHL, 4 bits):** The length of the header measured in **32-bit words**. Minimum value is `5` ($5 \times 4 = 20\text{ bytes}$).
3. **Type of Service / DSCP & ECN (8 bits):** Differentiated Services Code Point (QoS class) and Explicit Congestion Notification.
4. **Total Length (16 bits):** Entire datagram length (header + payload) in bytes. Maximum theoretical size is $2^{16} - 1 = 65,535\text{ bytes}$.
5. **Identification (16 bits):** Unique sequence identifier assigned by the source to group all fragments of a single original datagram.
6. **Flags (3 bits):**
   - Bit 0: Reserved (must be 0).
   - Bit 1: **DF (Don't Fragment)**. If set to 1, routers must not fragment; if MTU is exceeded, packet is dropped and ICMP "Fragmentation Needed" is sent.
   - Bit 2: **MF (More Fragments)**. `1` indicates more fragments follow; `0` indicates the final fragment.
7. **Fragment Offset (13 bits):** Position of this fragment's data in the original datagram, measured in **units of 8 bytes (64 bits)**.
8. **Time to Live (TTL, 8 bits):** Hop counter decremented by 1 at every router. Prevents packets from circulating infinitely during routing loops. If TTL hits 0, the packet is discarded and ICMP "Time Exceeded" is returned.
9. **Protocol (8 bits):** Upper-layer transport protocol:
   - `1`: ICMP
   - `6`: TCP
   - `17`: UDP
10. **Header Checksum (16 bits):** Integrity verification covering only the 20-to-60 byte header.
11. **Source IP Address (32 bits):** Originating host IP.
12. **Destination IP Address (32 bits):** Target host IP.
13. **Options & Padding:** Variable length, padded to 32-bit boundary.

---

### 2.3 Maximum Transmission Unit (MTU) & The Need for Fragmentation
Each link-layer technology has a physical **Maximum Transmission Unit (MTU)**:
- Standard Ethernet MTU $= 1500\text{ bytes}$.
- Wi-Fi MTU $\approx 2304\text{ bytes}$.
- PPPoE MTU $= 1492\text{ bytes}$.

When a router receives a datagram of size $3000\text{ bytes}$ that must exit over an Ethernet link with $\text{MTU} = 1500\text{ bytes}$, the router must split the payload into multiple smaller fragments. Each fragment receives its own independent IPv4 header. Reassembly occurs **only at the final destination host**, never at intermediate routers.

---

## 3. The 16-Bit Internet Header Checksum Algorithm

### 3.1 One's-Complement Arithmetic & End-Around Carry Folding
In standard two's-complement arithmetic, negative numbers use sign bits and overflow carries are discarded. In **one's-complement arithmetic**:
1. Numbers are summed.
2. Any carry bits that overflow past bit 15 (into bit 16 or beyond) are **wrapped around and added back** to the lowest bit:
   $$\text{folded sum} = (total \land \text{0xFFFF}) + (total \gg 16)$$
3. The final 16-bit sum is inverted bitwise (one's complement):
   $$\text{Checksum} = (\sim \text{folded sum}) \land \text{0xFFFF}$$

### 3.2 Verification Property: Why a Valid Header Folds to `0xFFFF`
A sender computes $C = \sim \sum \text{Words}$. When the sender writes $C$ into the header and transmits it:
$$\sum_{\text{all words incl } C} \text{Words} = \left(\sum_{\text{data}} \text{Words}\right) + \sim\left(\sum_{\text{data}} \text{Words}\right)$$
By definition of one's complement, adding any binary number to its bitwise negation produces **all ones (`0xFFFF`)**:
$$\text{Recomputed Sum} = \mathbf{\text{0xFFFF}}$$
Taking the one's complement of `0xFFFF` gives $\mathbf{\text{0x0000}}$ ($0$). Thus, a receiver can verify integrity simply by summing all ten 16-bit words: if the sum equals `0xFFFF` (or complement equals 0), the header is intact!

---

### 3.3 Incremental Checksum Updating (RFC 1624)
Because routers decrement TTL by 1 at every hop, recomputing the entire 20-byte checksum from scratch would waste massive CPU cycles. In RFC 1624, routers update the checksum incrementally:
$$C_{\text{new}} = \sim (\sim C_{\text{old}} + \sim m + m')$$
where $m$ is the old TTL word and $m'$ is the new TTL word.

---

## 4. Part A: Wireshark Header Analysis & Field Reconstruction

### 4.1 Dissection of Clean Packet 1
Raw Header Hex String:
`45 00 00 28 1C 46 00 00 40 11 DB 10 C0 A8 01 0A C0 A8 01 14`

- Byte 0: `0x45` $\implies$ Version: **4**, IHL: **5** ($5 \times 4 = \mathbf{20\text{ bytes}}$).
- Byte 1: `0x00` $\implies$ DSCP: **0**, ECN: **0**.
- Bytes 2–3: `0x0028` $\implies$ Total Length: **40 bytes** (20 bytes header + 20 bytes UDP/payload).
- Bytes 4–5: `0x1C46` $\implies$ Identification: **`0x1C46`** ($7238$ decimal).
- Bytes 6–7: `0x0000` $\implies$ Flags: **`0x0`** (DF=0, MF=0), Fragment Offset: **0**.
- Byte 8: `0x40` $\implies$ Time to Live: **64**.
- Byte 9: `0x11` $\implies$ Protocol: **17** (**UDP**).
- Bytes 10–11: `0xDB10` $\implies$ Header Checksum: **`0xDB10`**.
- Bytes 12–15: `C0 A8 01 0A` $\implies$ Source IP: **`192.168.1.10`**.
- Bytes 16–19: `C0 A8 01 14` $\implies$ Destination IP: **`192.168.1.20`**.

---

### 4.2 Cross-Reconciliation Table

| Field Name | Raw Hex Bytes | Decoded Value | Wireshark Match |
| :--- | :--- | :--- | :---: |
| **Version** | High nibble byte 0 (`4`) | IPv4 | Verified |
| **Header Length (IHL)**| Low nibble byte 0 (`5`) | 20 bytes | Verified |
| **Total Length** | `00 28` | 40 bytes | Verified |
| **Identification** | `1C 46` | `0x1C46` (7238) | Verified |
| **Flags** | High 3 bits bytes 6-7 | `0x0` (All Clear) | Verified |
| **Fragment Offset** | Low 13 bits bytes 6-7 | 0 bytes | Verified |
| **Time to Live (TTL)**| `40` | 64 hops | Verified |
| **Protocol** | `11` | UDP (17) | Verified |
| **Header Checksum** | `DB 10` | `0xDB10` (Correct) | Verified |
| **Source Address** | `C0 A8 01 0A` | 192.168.1.10 | Verified |
| **Destination Address**| `C0 A8 01 14` | 192.168.1.20 | Verified |

---

## 5. Part B: Mathematical Checksum Verification & TTL Corruption

### 5.1 Manual 16-Bit Word Addition of Clean Header
The nine 16-bit words (skipping checksum field at bytes 10–11) are:

| Word Index & Byte Offset | Hex Value |
|:---|:---:|
| Word 1 (Bytes 0–1) | `0x4500` |
| Word 2 (Bytes 2–3) | `0x0028` |
| Word 3 (Bytes 4–5) | `0x1C46` |
| Word 4 (Bytes 6–7) | `0x0000` |
| Word 5 (Bytes 8–9) | `0x4011` |
| Word 6 (Bytes 12–13) | `0xC0A8` |
| Word 7 (Bytes 14–15) | `0x010A` |
| Word 8 (Bytes 16–17) | `0xC0A8` |
| Word 9 (Bytes 18–19) | `0x0114` |
| **Sum** | **`0x224EB`** |

#### Folding Carries:
The sum `0x224EB` exceeds 16 bits (carry $= \text{0x2}$):
$$\text{folded} = \text{0x24EB} + \text{0x2} = \mathbf{\text{0x24ED}}$$

#### Taking One's Complement:
$$\text{Computed Checksum} = (\sim \text{0x24ED}) \land \text{0xFFFF} = \mathbf{\text{0xDB10}}$$

- Stored Checksum: `0xDB10`
- Computed Checksum: `0xDB10`
- **Result:** $\mathbf{\text{VALID (MATCH)}}$.

---

### 5.2 Simulating Router TTL Decrement & Checksum Invalidation
In Packet 2, the TTL byte at offset 8 was decremented from `0x40` ($64$) to `0x3F` ($63$), but the sender or router failed to recompute the checksum, leaving `0xDB10`:
$$\text{Word 5 becomes: } \text{0x3F11} \quad (\text{difference of } -0x0100)$$

$$\text{New Sum} = \text{0x224EB} - \text{0x0100} = \text{0x223EB}$$
$$\text{folded} = \text{0x23EB} + \text{0x2} = \text{0x23ED}$$
$$\text{New Computed Checksum} = \sim \text{0x23ED} = \mathbf{\text{0xDC10}}$$

- Stored Checksum: `0xDB10`
- Computed Checksum: `0xDC10`
- **Result:** $\mathbf{\text{INVALID (MISMATCH)}} \implies$ **Packet Discarded!**

---

### 5.3 Wireshark Checksum Validation Setting
In Wireshark:
`Edit -> Preferences -> Protocols -> IPv4 -> Enable "Validate the IPv4 header checksum"`
When enabled, Wireshark highlights Packet 2 with an explicit warning banner:
> `[Expert Info (Warning/Checksum): Bad IPv4 Checksum 0xdb10 [should be 0xdc10]]`

---

## 6. Part C: IP Datagram Fragmentation & Reassembly

### 6.1 The Identification, Flags (DF, MF) and Fragment Offset Triple
A large original datagram is fragmented into three pieces, all sharing Identification **`0x4A3F`**:

| Fragment # | Identification | More Fragments (MF) | Fragment Offset (units) | Offset in Bytes ($\text{units} \times 8$) | Total Length | Payload Length |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | `0x4A3F` | **1** | 0 | $0 \times 8 = \mathbf{0}$ | 1500 | $1500 - 20 = \mathbf{1480}$ |
| **2** | `0x4A3F` | **1** | 185 | $185 \times 8 = \mathbf{1480}$ | 1500 | $1500 - 20 = \mathbf{1480}$ |
| **3** | `0x4A3F` | **0** | 370 | $370 \times 8 = \mathbf{2960}$ | 60 | $60 - 20 = \mathbf{40}$ |

---

### 6.2 Reassembly Algorithm & Math Trace of Fragments 3, 4, and 5
The receiver reconstructs the payload ranges:
1. **Fragment 1:** Offset $0 \to$ Starts at byte 0. Length 1480 $\implies$ **Bytes [0 to 1479]**.
2. **Fragment 2:** Offset $185 \times 8 = 1480 \to$ Starts at byte 1480. Length 1480 $\implies$ **Bytes [1480 to 2959]**.
3. **Fragment 3:** Offset $370 \times 8 = 2960 \to$ Starts at byte 2960. Length 40 $\implies$ **Bytes [2960 to 2999]**.

```
Original Datagram Payload: 3000 Bytes
[0 ----------------- 1479] [1480 ----------------- 2959] [2960 ------- 2999]
     Fragment 1 (MF=1)             Fragment 2 (MF=1)           Fragment 3 (MF=0)
```

### 6.3 Verification of Reassembled 3000-Byte Payload
- The byte ranges form a contiguous block: $[0, 1479] \cup [1480, 2959] \cup [2960, 2999] = [0, 2999]$.
- Total length: $2999 + 1 = \mathbf{3000\text{ bytes}}$.
- Fragment 3 has **$\text{MF} = 0$**, marking the exact end of the datagram.
- Reassembly status: $\mathbf{\text{COMPLETE}}$.

---

## 7. Part D: Deep-Dive Analysis (Answering Lab Questions)

### 7.1 Why TTL Forces Checksum Recomputation at Every Hop
**Answer:**
1. The **Time to Live (TTL)** field is decremented by at least 1 at every single router that forwards the packet to prevent packets from endlessly looping during routing transients.
2. Because the TTL field (byte offset 8) is an integral component of the 20-byte IPv4 header, altering the TTL value changes the 16-bit word sum of the header.
3. Therefore, **every router must update or recompute the IPv4 Header Checksum at every hop**. If a router decrements the TTL but forwards the datagram with the old checksum (as simulated in Part B), the next downstream router or destination host will detect a checksum mismatch and immediately drop the packet.

---

### 7.2 The 8-Byte Boundary Rule: Why Fragment Offset Units are 8 Bytes
**Answer:**
The **Fragment Offset** field in the IPv4 header is allocated exactly **13 bits**.
- If the offset counted individual bytes, a 13-bit field could only represent offsets up to $2^{13} - 1 = 8,191\text{ bytes}$.
- However, the **Total Length** field is 16 bits wide, allowing IPv4 datagrams to reach $65,535\text{ bytes}$ ($\approx 64\text{ KB}$).
- To allow a 13-bit offset field to span the full $65,535\text{ byte}$ space, the designers of IPv4 scaled the offset by a factor of 8 ($2^3$):
  $$8 \times 8192 = 65,536\text{ bytes}$$
- **Direct Consequence:** Because the offset is expressed in units of 8-byte blocks, **every fragment payload (except the final fragment) must have a length that is an exact integer multiple of 8 bytes**.

---

### 7.3 Why the Checksum Covers Only the Header (and Why IPv6 Dropped It)
**Answer:**
1. **Router Forwarding Efficiency:** Routers only inspect and modify header fields (TTL, IP addresses, QoS). If the IP checksum covered the multi-kilobyte payload, every intermediate router in the core of the Internet would have to compute a checksum over millions of payload bytes per second, creating a massive throughput bottleneck.
2. **End-to-End Argument & Dual Protection:** Payload integrity is already protected:
   - **Hop-by-hop at Layer 2:** Ethernet FCS (CRC-32) detects physical transmission errors.
   - **End-to-end at Layer 4:** TCP and UDP compute end-to-end checksums over the payload and pseudo-header.
3. **The IPv6 Architectural Evolution:** Recognizing that intermediate header checksums are redundant and CPU-intensive, **IPv6 completely eliminated the header checksum**. IPv6 relies exclusively on Layer 2 CRCs and mandatory Layer 4 TCP/UDP checksums, drastically accelerating router forwarding performance.

---

## 8. Software Architecture & Python Implementation (`checksumVerify.py`)

The script `checksumVerify.py` implements:
- `verify_ip_checksum(header)`:
  - Extracts stored checksum at bytes 10–11.
  - Sums remaining 16-bit words.
  - Folds carries: `(total & 0xFFFF) + (total >> 16)`.
  - Computes one's complement: `~total & 0xFFFF`.
  - Returns `(stored, computed, valid)`.
- `reassemble(fragments)`:
  - Computes byte ranges: $[offset \times 8, offset \times 8 + length - 1]$.
  - Identifies final fragment from $MF = 0$.
  - Returns `(ranges, total_length, complete)`.

---

## 9. Comprehensive Viva & Exam Preparation Guide

### Q1: What happens if an IPv4 packet's TTL hits zero while inside a router?
**Answer:** The router immediately discards the packet. It generates an **ICMP Type 11 (Time Exceeded, Code 0 - Time to Live exceeded in transit)** error message and sends it back to the original source IP address. (This exact mechanism is what powers the `traceroute` command).

### Q2: Why does IP fragmentation happen at routers, but reassembly happens only at the destination?
**Answer:** Different fragments of the same datagram may take completely different geographic paths through the network due to dynamic routing or load balancing. Intermediate routers cannot guarantee they will see all fragments. Only the final destination host is guaranteed to receive all pieces.

### Q3: What is the "Don't Fragment" (DF) bit used for in modern networks?
**Answer:** It is used for **Path MTU Discovery (PMTUD, RFC 1191)**. A host sets DF=1 and sends full-size packets. If any intermediate router cannot forward the packet without fragmenting, it drops the packet and returns an ICMP "Fragmentation Needed" message containing that link's MTU. The host adjusts its Maximum Segment Size (MSS) accordingly, completely avoiding the overhead of IP fragmentation.

---
*End of Lab 9 Report · Prepared for CS353 Computer Networks*
