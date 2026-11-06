# CS353: The MAC Sublayer (IEEE 802.11 Wi-Fi Frame Decoding)
## Comprehensive Lab Report, Theory Guide & Implementation Manual
**Course:** CS353 · Computer Networks · Week 7 / Lab 7  
**Topic:** MAC Sublayer / IEEE 802.11 Protocol Architecture, Frame Control, Address Roles & NAV Virtual Carrier Sensing  
**System Implemented:** 802.11 Hex Byte Parser, Frame Dissector, and RTS/CTS/NAV Protocol Analyzer in Python

---

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [Theoretical Foundations of IEEE 802.11 MAC Architecture](#2-theoretical-foundations-of-ieee-80211-mac-architecture)
   - [2.1 Wireless Media Challenges: Half-Duplex & Hidden Terminals](#21-wireless-media-challenges-half-duplex--hidden-terminals)
   - [2.2 CSMA/CA (Collision Avoidance) and the RTS/CTS Handshake](#22-csmaca-collision-avoidance-and-the-rtscts-handshake)
   - [2.3 Network Allocation Vector (NAV) & Virtual Carrier Sensing](#23-network-allocation-vector-nav--virtual-carrier-sensing)
3. [The IEEE 802.11 MAC Frame Architecture](#3-the-ieee-80211-mac-frame-architecture)
   - [3.1 General Frame Layout (Headers, Addresses, Payload, FCS)](#31-general-frame-layout-headers-addresses-payload-fcs)
   - [3.2 The 2-Byte Frame Control Field (Type, Subtype, Flags)](#32-the-2-byte-frame-control-field-type-subtype-flags)
   - [3.3 The Four-Address Model & The ToDS / FromDS Matrix](#33-the-four-address-model--the-tods--fromds-matrix)
4. [Part 1: Manual Decoding of Sample Frames (F1 & F3)](#4-part-1-manual-decoding-of-sample-frames-f1--f3)
   - [4.1 Detailed Byte-by-Byte Manual Decoding of Frame F1](#41-detailed-byte-by-byte-manual-decoding-of-frame-f1)
   - [4.2 Detailed Byte-by-Byte Manual Decoding of Frame F3](#42-detailed-byte-by-byte-manual-decoding-of-frame-f3)
   - [4.3 Official Verification Table](#43-official-verification-table)
5. [Part 2: Automated 802.11 Parser Implementation (`parser.py`)](#5-part-2-automated-80211-parser-implementation-parserpy)
   - [5.1 Bitwise Bit-Field Extraction Logic](#51-bitwise-bit-field-extraction-logic)
   - [5.2 Little-Endian Duration and Sequence Dissection](#52-little-endian-duration-and-sequence-dissection)
   - [5.3 Decoded Outputs for All Six Captured Frames (F1–F6)](#53-decoded-outputs-for-all-six-captured-frames-f1f6)
6. [Part 3: Protocol Interpretation & Deep-Dive Analysis (C3)](#6-part-3-protocol-interpretation--deep-dive-analysis-c3)
   - [6.1 The F3-F4-F5 Exchange & Decreasing Duration Fields](#61-the-f3-f4-f5-exchange--decreasing-duration-fields)
   - [6.2 The Hidden Terminal Solution via F4 (CTS) & NAV Setting](#62-the-hidden-terminal-solution-via-f4-cts--nav-setting)
   - [6.3 Duplicate Frame Rejection via Retry Bit & Sequence Number](#63-duplicate-frame-rejection-via-retry-bit--sequence-number)
   - [6.4 Why Frame F6 Requires a 4th Address (WDS Wireless Bridging)](#64-why-frame-f6-requires-a-4th-address-wds-wireless-bridging)
7. [Comprehensive Viva & Exam Preparation Guide](#7-comprehensive-viva--exam-preparation-guide)

---

## 1. Executive Summary

While wired Ethernet (IEEE 802.3) relies on Collision Detection (CSMA/CD), wireless radios cannot listen to incoming signals while transmitting because their local transmitter power completely overpowers incoming microvolt signals ($100\text{ dB}$ difference). Consequently, Wi-Fi (IEEE 802.11) utilizes **Carrier Sense Multiple Access with Collision Avoidance (CSMA/CA)**.

In Lab 7, we study, decode, and parse the complex **IEEE 802.11 MAC Sublayer frame format**. We analyze:
1. The 16-bit **Frame Control** field (Protocol Version, Type, Subtype, and 8 discrete control flags).
2. The dynamic **Four-Address Architecture** governed by the `ToDS` and `FromDS` bits.
3. The **RTS/CTS 4-way transaction** and the **Network Allocation Vector (NAV)** countdown mechanism used to solve the famous **Hidden Terminal Problem**.
4. The 4-address **Wireless Distribution System (WDS)** frame format used for AP-to-AP mesh bridging.

```
+--------------------------------------------------------------------------------------------------+
|                                  IEEE 802.11 MAC FRAME ARCHITECTURE                              |
|                                                                                                  |
|  2 Bytes    2 Bytes   6 Bytes   6 Bytes   6 Bytes   2 Bytes   6 Bytes   0-2312 B    4 Bytes      |
| +---------+---------+---------+---------+---------+---------+---------+-----------+------------+ |
| | Frame   |Duration/| Address | Address | Address |Sequence | Address |   Frame   |    FCS     | |
| | Control |   ID    |    1    |    2    |    3    | Control |    4    |  Payload  |  (CRC-32)  | |
| +---------+---------+---------+---------+---------+---------+---------+-----------+------------+ |
|      │                                                           ▲                               |
|      ▼                                                           │ (Only present if              |
| +───────────────────────────────────────────────────────────+    │  ToDS=1 and FromDS=1,         |
| | Protocol | Type | Subtype | To |From|More|Retry|Pwr |More|Prot|Order│    │  e.g. WDS mesh link)       |
| | Version  | (2b) |  (4b)   | DS | DS |Frag| (1b)|Mgmt|Data| (1b)|(1b)│                                |
| |   (2b)   |      |         |(1b)|(1b)|(1b)|     |(1b)|(1b)|    |    │                                |
| +───────────────────────────────────────────────────────────+                                    |
+--------------------------------------------------------------------------------------------------+
```

---

## 2. Theoretical Foundations of IEEE 802.11 MAC Architecture

### 2.1 Wireless Media Challenges: Half-Duplex & Hidden Terminals
Wireless transmissions suffer from two unique physical phenomena that do not exist on wired cables:
1. **Half-Duplex Radio Inability to Detect Collisions:** A transceiver transmits at $+20\text{ dBm}$ ($100\text{ mW}$) while received signals from distant nodes arrive at $-80\text{ dBm}$ ($10\text{ pW}$). The transmitter cannot hear incoming collisions over its own transmission.
2. **The Hidden Terminal Problem:**
   ```
   [ Station A ] <─────── (Wireless Range) ───────> [ Access Point ] <─────── (Wireless Range) ───────> [ Station C ]
   ```
   Station A and Station C are out of radio range of each other, but both can reach the Access Point. If A and C sense the medium, both hear silence and transmit simultaneously. Their frames collide at the AP. Station A is "hidden" from Station C.

### 2.2 CSMA/CA (Collision Avoidance) and the RTS/CTS Handshake
To eliminate hidden terminal collisions, IEEE 802.11 introduces an optional 4-way channel reservation protocol:
1. **RTS (Request to Send):** Transmitter sends a short 20-byte control frame requesting channel reservation.
2. **CTS (Clear to Send):** Destination AP broadcasts a 14-byte CTS frame announcing that the channel is reserved for the transmitter.
3. **DATA:** Transmitter sends the actual data payload frame.
4. **ACK:** Destination sends an immediate acknowledgment.

### 2.3 Network Allocation Vector (NAV) & Virtual Carrier Sensing
Every 802.11 frame contains a 16-bit **Duration/ID** field specifying how many microseconds ($\mu\text{s}$) the radio channel will remain occupied until the entire exchange (including SIFS intervals and ACK) finishes.
- Any neighboring station that overhears an RTS or CTS reads this Duration field.
- The station updates an internal countdown timer called the **Network Allocation Vector (NAV)**.
- While the NAV timer is non-zero, the station treats the medium as **virtually busy** and defers all transmissions, completely preventing hidden terminal collisions!

---

## 3. The IEEE 802.11 MAC Frame Architecture

### 3.1 General Frame Layout (Headers, Addresses, Payload, FCS)
A complete 802.11 frame consists of up to 30 bytes of header:
- **Frame Control (2 bytes):** Dictates protocol version, frame type, and 8 control flags.
- **Duration/ID (2 bytes):** Duration in $\mu\text{s}$ (stored in little-endian order).
- **Addresses 1 to 4 (6 bytes each):** 48-bit IEEE MAC addresses.
- **Sequence Control (2 bytes):** 4-bit Fragment Number + 12-bit Sequence Number.
- **Payload:** LLC/SNAP encapsulation and user data (e.g. IPv4 packet).
- **FCS (4 bytes):** CRC-32 integrity check.

---

### 3.2 The 2-Byte Frame Control Field (Type, Subtype, Flags)

```
Byte 0 (Bit 0 to Bit 7):
[ Protocol Version (2 bits) ] [ Type (2 bits) ] [ Subtype (4 bits) ]

Byte 1 (Bit 0 to Bit 7):
[ ToDS ][ FromDS ][ MoreFrag ][ Retry ][ PwrMgmt ][ MoreData ][ Protected ][ Order ]
```

#### Frame Types (`Bits 2-3` of Byte 0):
- `00`: **Management Frame** (Beacons, Association Request/Response, Probe Request/Response).
- `01`: **Control Frame** (RTS = `1011`, CTS = `1100`, ACK = `1101`).
- `10`: **Data Frame** (Standard user payload = `0000`, QoS Data = `1000`).

---

### 3.3 The Four-Address Model & The ToDS / FromDS Matrix
Unlike Ethernet which only requires Source and Destination MAC addresses, an 802.11 frame may traverse wireless access points, requiring distinction between the **wireless transmitter/receiver** (hops) and the **ultimate end-host sender/destination**:

| ToDS | FromDS | Network Context | Address 1 (RA) | Address 2 (TA) | Address 3 | Address 4 |
| :---: | :---: | :--- | :--- | :--- | :--- | :--- |
| **0** | **0** | **Ad-hoc (IBSS)**: Direct station-to-station | Destination (DA) | Source (SA) | BSSID | *(Not used)* |
| **1** | **0** | **To AP (Uplink)**: Client sending into DS | Receiver / BSSID | Source (SA) | Destination (DA)| *(Not used)* |
| **0** | **1** | **From AP (Downlink)**: AP sending to Client | Destination (DA) | Transmitter / BSSID | Source (SA) | *(Not used)* |
| **1** | **1** | **WDS (Mesh Bridge)**: AP-to-AP forwarding | Receiver AP (RA) | Transmitter AP (TA) | Destination (DA)| Source (SA) |

---

## 4. Part 1: Manual Decoding of Sample Frames (F1 & F3)

### 4.1 Detailed Byte-by-Byte Manual Decoding of Frame F1
Hex Stream:
`08 01 2c 00 00 1a 2b 3c 4d 5e a4 83 e7 11 22 33 00 50 56 aa bb cc 30 1d aa aa 03 ...`

1. **Byte 0 (`0x08` = `0000 1000` in binary):**
   - Bits 0–1 (Protocol Version): `00` $\implies$ **Version 0**
   - Bits 2–3 (Type): `10` $\implies$ **Type 2: Data Frame**
   - Bits 4–7 (Subtype): `0000` $\implies$ **Subtype 0: Data**
2. **Byte 1 (`0x01` = `0000 0001` in binary):**
   - Bit 0 (`ToDS`): `1` $\implies$ **ToDS = 1**
   - Bit 1 (`FromDS`): `0` $\implies$ **FromDS = 0**
   - Bits 2–7 (Other flags): `0` $\implies$ No other flags set.
3. **Bytes 2–3 (`2c 00`):**
   - Little-endian 16-bit integer: `0x002c` = **$44\text{ }\mu\text{s}$ Duration**.
4. **Addresses (ToDS=1, FromDS=0 Context: Uplink to AP):**
   - **Address 1 (BSSID / RA):** Bytes 4–9: `00:1a:2b:3c:4d:5e` (Access Point MAC)
   - **Address 2 (SA / Source Client):** Bytes 10–15: `a4:83:e7:11:22:33` (Client MAC)
   - **Address 3 (DA / Final Destination):** Bytes 16–21: `00:50:56:aa:bb:cc` (Wired Server MAC)
5. **Bytes 22–23 (`30 1d`):**
   - Little-endian 16-bit integer: `0x1d30`
   - Bits 0–3 (Fragment Number): `0x0` = **0**
   - Bits 4–15 (Sequence Number): `0x1d3` = **467**
6. **LLC/SNAP Header (Bytes 24–31):**
   - `aa aa 03 00 00 00 08 00` $\implies$ EtherType `0x0800` (**IPv4 Protocol**).

---

### 4.2 Detailed Byte-by-Byte Manual Decoding of Frame F3
Hex Stream:
`b4 00 5e 01 00 1a 2b 3c 4d 5e a4 83 e7 11 22 33`

1. **Byte 0 (`0xb4` = `1011 0100` in binary):**
   - Bits 0–1 (Protocol Version): `00` $\implies$ **Version 0**
   - Bits 2–3 (Type): `01` $\implies$ **Type 1: Control Frame**
   - Bits 4–7 (Subtype): `1011` $\implies$ **Subtype 11: RTS (Request to Send)**
2. **Byte 1 (`0x00` = `0000 0000` in binary):**
   - ToDS = 0, FromDS = 0. No flags set.
3. **Bytes 2–3 (`5e 01`):**
   - Little-endian 16-bit integer: `0x015e` = **$350\text{ }\mu\text{s}$ Duration**.
4. **Addresses (RTS Control Frame Format: Exactly 2 Addresses):**
   - **Address 1 (RA / Receiver AP):** Bytes 4–9: `00:1a:2b:3c:4d:5e`
   - **Address 2 (TA / Transmitter Station):** Bytes 10–15: `a4:83:e7:11:22:33`
   - Address 3: **None** (RTS carries no Address 3)
5. **Sequence Control:** **None** (Control frames carry no sequence numbers).

---

### 4.3 Official Verification Table

| Field | Frame F1 | Frame F3 |
| :--- | :--- | :--- |
| **Type / Subtype** | Data / Data (`Type 2, Subtype 0`) | Control / RTS (`Type 1, Subtype 11`) |
| **ToDS, FromDS** | `ToDS = 1, FromDS = 0` | `ToDS = 0, FromDS = 0` |
| **Other Flags Set** | None | None |
| **Duration ($\mu\text{s}$)** | **$44\text{ }\mu\text{s}$** | **$350\text{ }\mu\text{s}$** |
| **Address 1 (Role)** | `00:1a:2b:3c:4d:5e` (**BSSID / RA**) | `00:1a:2b:3c:4d:5e` (**RA - Receiver**) |
| **Address 2 (Role)** | `a4:83:e7:11:22:33` (**SA - Source Station**) | `a4:83:e7:11:22:33` (**TA - Transmitter**) |
| **Address 3 (Role)** | `00:50:56:aa:bb:cc` (**DA - Final Destination**) | *(Not Present)* |
| **Sequence / Fragment** | **Sequence No. 467**, Fragment No. 0 | *(Not Present)* |

---

## 5. Part 2: Automated 802.11 Parser Implementation (`parser.py`)

### 5.1 Bitwise Bit-Field Extraction Logic
The core parsing logic cleanly isolates bitfields using bitwise masks and right-shifts:
```python
fc0, fc1 = b[0], b[1]
protocol_version = fc0 & 0b00000011
type_val         = (fc0 & 0b00001100) >> 2
subtype_val      = (fc0 & 0b11110000) >> 4

tods       = (fc1 & 0b00000001)
fromds     = (fc1 & 0b00000010) >> 1
more_frag  = (fc1 & 0b00000100) >> 2
retry      = (fc1 & 0b00001000) >> 3
power_mgmt = (fc1 & 0b00010000) >> 4
more_data  = (fc1 & 0b00100000) >> 5
protected  = (fc1 & 0b01000000) >> 6
order      = (fc1 & 0b10000000) >> 7
```

### 5.2 Little-Endian Duration and Sequence Dissection
```python
# Duration is 16-bit unsigned little-endian integer
duration = int.from_bytes(b[2:4], byteorder='little')

# Sequence Control is 16-bit unsigned little-endian integer at offset 22
seq_ctrl = int.from_bytes(b[22:24], byteorder='little')
frag_num = seq_ctrl & 0x000F
seq_num  = (seq_ctrl & 0xFFF0) >> 4
```

### 5.3 Decoded Outputs for All Six Captured Frames (F1–F6)

- **Frame F1 (Data):** Type: Data (0), Flags: `['ToDS']`, Duration: $44\text{ }\mu\text{s}$, Addr1: BSSID (`00:1a:2b:3c:4d:5e`), Addr2: SA (`a4:83:e7:11:22:33`), Addr3: DA (`00:50:56:aa:bb:cc`), Seq: 467, Frag: 0, EtherType: `0x0800` (IPv4).
- **Frame F2 (Data with Retry):** Type: Data (0), Flags: `['FromDS', 'Retry']`, Duration: $44\text{ }\mu\text{s}$, Addr1: DA (`a4:83:e7:11:22:33`), Addr2: BSSID (`00:1a:2b:3c:4d:5e`), Addr3: SA (`00:50:56:aa:bb:cc`), Seq: 467, Frag: 0.
- **Frame F3 (RTS):** Type: Control (RTS), Flags: `[]`, Duration: **$350\text{ }\mu\text{s}$**, Addr1: RA (`00:1a:2b:3c:4d:5e`), Addr2: TA (`a4:83:e7:11:22:33`).
- **Frame F4 (CTS):** Type: Control (CTS), Flags: `[]`, Duration: **$284\text{ }\mu\text{s}$**, Addr1: RA (`a4:83:e7:11:22:33`).
- **Frame F5 (ACK):** Type: Control (ACK), Flags: `[]`, Duration: **$0\text{ }\mu\text{s}$**, Addr1: RA (`a4:83:e7:11:22:33`).
- **Frame F6 (WDS 4-Address Data):** Type: Data (0), Flags: `['ToDS', 'FromDS', 'More Frag']`, Duration: $44\text{ }\mu\text{s}$, Addr1: RA (`02:11:22:33:44:55`), Addr2: TA (`02:66:77:88:99:aa`), Addr3: DA (`00:50:56:aa:bb:cc`), Addr4: SA (`a4:83:e7:11:22:33`).

---

## 6. Part 3: Protocol Interpretation & Deep-Dive Analysis (C3)

### 6.1 The F3-F4-F5 Exchange & Decreasing Duration Fields
Frames F3 (RTS), F4 (CTS), and F5 (ACK) form an atomic channel reservation transaction:
- **Sender of F3 (RTS):** Station `a4:83:e7:11:22:33` $\longrightarrow$ **Receiver:** AP `00:1a:2b:3c:4d:5e`.
- **Sender of F4 (CTS):** AP `00:1a:2b:3c:4d:5e` $\longrightarrow$ **Receiver:** Station `a4:83:e7:11:22:33`.
- **Sender of F5 (ACK):** AP `00:1a:2b:3c:4d:5e` $\longrightarrow$ **Receiver:** Station `a4:83:e7:11:22:33`.

#### Why the Duration Field Drops Continuously:
The Duration field reserves the channel for the **remainder of the multi-frame exchange**:
1. In **F3 (RTS)**, Duration $= 350\text{ }\mu\text{s}$: Covers the entire transaction:
   $$\text{Duration}_{\text{RTS}} = T_{\text{SIFS}} + T_{\text{CTS}} + T_{\text{SIFS}} + T_{\text{DATA}} + T_{\text{SIFS}} + T_{\text{ACK}} = 350\text{ }\mu\text{s}$$
2. In **F4 (CTS)**, Duration $= 284\text{ }\mu\text{s}$: The RTS and first SIFS have elapsed:
   $$\text{Duration}_{\text{CTS}} = \text{Duration}_{\text{RTS}} - (T_{\text{CTS}} + T_{\text{SIFS}}) = 284\text{ }\mu\text{s}$$
3. In **F5 (ACK)**, Duration $= 0\text{ }\mu\text{s}$: The transmission is complete; the channel is immediately released!

---

### 6.2 The Hidden Terminal Solution via F4 (CTS) & NAV Setting
A neighboring station that cannot hear the sender Station (F3) will hear the AP's broadcast of **F4 (CTS)**:
- **NAV Setting:** The station reads Duration $= \mathbf{284\text{ }\mu\text{s}}$ from F4 and programs its local Network Allocation Vector (NAV) timer to count down from $284\text{ }\mu\text{s}$.
- **Mechanism Implemented:** This implements **Virtual Carrier Sensing**. While the NAV timer is non-zero, the physical radio refuses to transmit, ensuring Station A can transmit its DATA frame to the AP without interference from the hidden station.

---

### 6.3 Duplicate Frame Rejection via Retry Bit & Sequence Number
Frame F2 has the **`Retry = 1`** flag set:
- When an ACK is lost in transit, the sender times out and retransmits the data frame with `Retry = 1` and the identical `Sequence Number = 467`.
- **Receiver Deduplication Algorithm:** The receiver maintains a cache of `(Transmitter MAC, Last Sequence Number)`. When F2 arrives, the receiver detects that sequence number 467 from this station has already been received and delivered to the network layer.
- Because `Retry = 1`, the receiver **discards the duplicate payload**, but immediately re-sends the ACK so the sender can finally advance its window!

---

### 6.4 Why Frame F6 Requires a 4th Address (WDS Wireless Bridging)
Frame F6 has **both `ToDS = 1` and `FromDS = 1`**:
```
[ Client SA ] ===> [ AP 1 (TA) ] ~ ~ (Wireless Link) ~ ~ > [ AP 2 (RA) ] ===> [ Server DA ]
```
- In standard infrastructure mode, a frame only has one wireless hop (either Client to AP, or AP to Client), requiring 3 addresses.
- In a **Wireless Distribution System (WDS)**, two wireless APs form a point-to-point wireless bridge connecting two separate wired LAN segments:
  - **Address 1 (RA):** Immediate receiving wireless bridge (`02:11:22:33:44:55`).
  - **Address 2 (TA):** Immediate transmitting wireless bridge (`02:66:77:88:99:aa`).
  - **Address 3 (DA):** Ultimate destination host (`00:50:56:aa:bb:cc`).
  - **Address 4 (SA):** Original source host (`a4:83:e7:11:22:33`).
- Without Address 4, AP 2 would not know which original host sent the packet when bridging it onto the destination wired Ethernet segment.

---

## 7. Comprehensive Viva & Exam Preparation Guide

### Q1: Why can't IEEE 802.11 use standard Ethernet CSMA/CD collision detection?
**Answer:** A Wi-Fi radio cannot detect collisions during transmission because its own transmitted signal radiation is overwhelmingly stronger than any incoming signal from a colliding node ($> 100\text{ dB}$ difference). The local receiver is completely saturated. Additionally, due to hidden terminals, a collision occurs at the receiver's antenna, not at the transmitter's antenna.

### Q2: What is the purpose of SIFS, DIFS, and EIFS in 802.11?
**Answer:** They are Interframe Spaces used to prioritize channel access:
- **SIFS (Short Interframe Space):** The shortest gap, giving highest priority to immediate control frames (ACK, CTS).
- **DIFS (Distributed Interframe Space):** Used for regular asynchronous data frames. A station must sense the medium idle for at least DIFS before starting backoff.
- **EIFS (Extended Interframe Space):** Used when a station receives an unreadable/corrupted frame, forcing it to defer longer to allow clean recovery.

### Q3: What is the difference between physical carrier sensing and virtual carrier sensing?
**Answer:**
- **Physical Carrier Sensing:** The hardware physical layer measures RF energy (Clear Channel Assessment, CCA) on the antenna to determine if a signal is currently present.
- **Virtual Carrier Sensing:** A logical timer (NAV) maintained by the MAC layer based on the Duration field declared in overheard RTS/CTS/Data frames. The station treats the medium as busy whenever $\text{NAV} > 0$.

### Q4: When is Address 4 present in an 802.11 frame?
**Answer:** Address 4 is present **if and only if both `ToDS = 1` and `FromDS = 1`**. This occurs exclusively in Wireless Distribution System (WDS) mesh links where frames travel wirelessly between two intermediate Access Points.

---
*End of Lab 7 Report · Prepared for CS353 Computer Networks*

