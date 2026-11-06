# CS353: Framing at the Data Link Layer
## Comprehensive Lab Report, Theory Guide & Implementation Manual
**Course:** CS353 · Computer Networks · Week 3 / Lab 3  
**Topic:** Data Link Layer / Framing Techniques, Byte Stuffing, Bit Stuffing & Resynchronization  
**System Implemented:** Byte Count Framing, Byte-Oriented Character Stuffing, and Bit-Oriented Stuffing in Python

---

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [Theoretical Foundations of Data Link Framing](#2-theoretical-foundations-of-data-link-framing)
   - [2.1 Why is Framing Necessary?](#21-why-is-framing-necessary)
   - [2.2 The Frame Synchronization Problem](#22-the-frame-synchronization-problem)
   - [2.3 Comparison of Major Framing Paradigms](#23-comparison-of-major-framing-paradigms)
3. [Part A: Byte Count Framing](#3-part-a-byte-count-framing)
   - [3.1 Framing Mechanism & Protocol Format](#31-framing-mechanism--protocol-format)
   - [3.2 Implementation Details (`byte_count_frame`, `byte_count_parse`)](#32-implementation-details-byte_count_frame-byte_count_parse)
   - [3.3 The Catastrophic Desynchronization Flaw](#33-the-catastrophic-desynchronization-flaw)
4. [Part B: Byte Stuffing (Character-Oriented Framing)](#4-part-b-byte-stuffing-character-oriented-framing)
   - [4.1 Flag and Escape Byte Delimiters (`0x7E`, `0x7D`)](#41-flag-and-escape-byte-delimiters-0x7e-0x7d)
   - [4.2 Sender Stuffing & Receiver Deframing State Machine](#42-sender-stuffing--receiver-deframing-state-machine)
   - [4.3 Error Recovery & Resynchronization Boundary](#43-error-recovery--resynchronization-boundary)
5. [Part C: Bit Stuffing (Bit-Oriented Framing / HDLC)](#5-part-c-bit-stuffing-bit-oriented-framing--hdlc)
   - [5.1 The Six-Consecutive-Ones Flag (`01111110`)](#51-the-six-consecutive-ones-flag-01111110)
   - [5.2 Five-Ones Rule Algorithm & Packing Logic](#52-five-ones-rule-algorithm--packing-logic)
   - [5.3 Distinction: Normal Data, Flag Pattern, and Abort Signal](#53-distinction-normal-data-flag-pattern-and-abort-signal)
6. [Part D: Resilience, Transmission Errors & Overhead Analysis](#6-part-d-resilience-transmission-errors--overhead-analysis)
   - [6.1 Single-Byte Corruption Simulation](#61-single-byte-corruption-simulation)
   - [6.2 Framing Overhead & Worst-Case Payload Expansion](#62-framing-overhead--worst-case-payload-expansion)
7. [Software Architecture & Python Implementation (`assignment3.py`)](#7-software-architecture--python-implementation-assignment3py)
8. [Comprehensive Viva & Exam Preparation Guide](#8-comprehensive-viva--exam-preparation-guide)

---

## 1. Executive Summary

The Physical Layer provides an unformatted stream of bits or bytes across a raw physical medium. It does not understand packets, characters, or messages. The **Data Link Layer** is responsible for transforming this raw bitstream into discrete units of communication called **frames**.

In Lab 3, we implement, benchmark, and stress-test the three classical framing algorithms used in computer networking:
1. **Byte Count Framing:** A length-prefix approach where each frame begins with a count of its payload length.
2. **Byte Stuffing (Character Stuffing):** Delimiting frames with sentinel `FLAG` bytes (`0x7E`) and escaping payload flags/escapes with `ESC` (`0x7D`).
3. **Bit Stuffing (HDLC / PPP Style):** Delimiting frames with the bit sequence `01111110` and stuffing a `0` after any sequence of five consecutive `1`s in the payload.

```
+--------------------------------------------------------------------------------------------------+
|                                    FRAMING PARADIGMS COMPARISON                                  |
|                                                                                                  |
| 1. BYTE COUNT:                                                                                   |
|    [ Length = 4 ] [ D1 ] [ D2 ] [ D3 ] [ D4 ] [ Length = 2 ] [ D1 ] [ D2 ]                      |
|                                                                                                  |
| 2. BYTE STUFFING:                                                                                |
|    [ 0x7E ] [ D1 ] [ 0x7D ] [ 0x7E ] [ D2 ] [ 0x7D ] [ 0x7D ] [ D3 ] [ 0x7E ]                    |
|      FLAG            ESC      STUFFED          ESC      STUFFED        FLAG                      |
|                                                                                                  |
| 3. BIT STUFFING:                                                                                 |
|    [ 01111110 ] ... 1 1 1 1 1 [ 0 ] 1 1 0 ... [ 01111110 ]                                      |
|       FLAG                    STUFFED 0            FLAG                                          |
+--------------------------------------------------------------------------------------------------+
```

---

## 2. Theoretical Foundations of Data Link Framing

### 2.1 Why is Framing Necessary?
A physical channel (copper, fibre, wireless) only sees continuous voltage transitions, light pulses, or radio waves:
- When does a packet begin?
- When does a packet end?
- How does the receiver distinguish user data from network control information?
- If noise corrupts the channel, how does the receiver recover frame boundaries without discarding the entire connection?

Without **framing**, a receiver cannot parse headers, compute error-checking checksums (CRC), or deliver packets to the network layer (IPv4/IPv6).

### 2.2 The Frame Synchronization Problem
Frame synchronization is the process by which a receiver identifies the exact start and end of a transmission frame. The central challenge is **transparency**:
> **The Transparency Challenge:** The user payload may contain any arbitrary binary sequence. If a payload happens to contain the exact bit pattern used to mark the end of a frame, the receiver must not prematurely terminate the frame.

### 2.3 Comparison of Major Framing Paradigms

| Framing Technique | Delimiting Strategy | Transparency Mechanism | Error Resilience | Modern Usage |
| :--- | :--- | :--- | :--- | :--- |
| **Byte Count** | Leading length integer | None needed (relies on count) | **Zero (Catastrophic desync)** | High-level RPCs, TLV fields |
| **Byte Stuffing** | `FLAG` byte (`0x7E`) | `ESC` byte prefix (`0x7D`) | Fast recovery at next `FLAG` | BISYNC, PPP (byte mode) |
| **Bit Stuffing** | Bit pattern `01111110` | Stuff `0` after five `1`s | Fast recovery at next `01111110` | HDLC, SDLC, USB, CAN bus |
| **Physical Coding** | Out-of-band symbol (e.g. 4B/5B) | Illegal code words | High (hardware detected) | Fast Ethernet, Gigabit Ethernet |

---

## 3. Part A: Byte Count Framing

### 3.1 Framing Mechanism & Protocol Format
In byte count framing, the header of each frame contains an integer specifying the number of bytes in that frame:
```
[ Count (1 Byte) ] [ Payload Byte 1 ] [ Payload Byte 2 ] ... [ Payload Byte N ]
```
The receiver reads the first byte ($C$), reads the subsequent $C$ bytes as payload, and immediately treats the $(C+1)$-th byte as the count for the next frame.

### 3.2 Implementation Details (`byte_count_frame`, `byte_count_parse`)
```python
def byte_count_frame(payload):
    if len(payload) > 255:
        raise ValueError("Payload cannot exceed 255 bytes")
    # Prepend 1-byte length prefix
    return [len(payload)] + list(payload)

def byte_count_parse(stream):
    payloads = []
    i = 0
    while i < len(stream):
        count = stream[i]
        i += 1
        # Check for truncated final frame
        if i + count > len(stream):
            break
        payload = stream[i : i + count]
        payloads.append(payload)
        i += count
    return payloads
```

### 3.3 The Catastrophic Desynchronization Flaw
The fundamental weakness of Byte Count framing is its vulnerability to transmission errors in the count field:
```
Transmitted Stream:
Frame 1: [Count = 5] [ A ] [ B ] [ C ] [ D ] [ E ]
Frame 2: [Count = 3] [ F ] [ G ] [ H ]
Frame 3: [Count = 4] [ I ] [ J ] [ K ] [ L ]

Stream bytes: [05, A, B, C, D, E, 03, F, G, H, 04, I, J, K, L]

Suppose a 1-bit error flips the first byte from 05 to 07:
Corrupted stream: [07, A, B, C, D, E, 03, F, G, H, 04, I, J, K, L]
```
1. The receiver reads count $= 7$.
2. It consumes `[A, B, C, D, E, 03, F]` as Frame 1's payload.
3. The next byte it reads as the count for Frame 2 is `G` (ASCII 71).
4. It attempts to read 71 bytes, running off the end of the buffer.
5. **Frame 1, Frame 2, and all future frames are permanently destroyed.** The receiver has no sentinel delimiter to resynchronize itself.

---

## 4. Part B: Byte Stuffing (Character-Oriented Framing)

### 4.1 Flag and Escape Byte Delimiters (`0x7E`, `0x7D`)
Byte stuffing solves the desynchronization problem by delimiting every frame with a dedicated sentinel **FLAG** byte:
- `FLAG = 0x7E` (Binary: `01111110`, ASCII `~`)
- `ESC  = 0x7D` (Binary: `01111101`, ASCII `}`)

```
[ FLAG ] [ Stuffed Payload Bytes ] [ FLAG ]
```

### 4.2 Sender Stuffing & Receiver Deframing State Machine

#### Sender Rules:
When encoding payload bytes:
1. If a byte is `FLAG` (`0x7E`), transmit `ESC` followed by `FLAG` (`[0x7D, 0x7E]`).
2. If a byte is `ESC` (`0x7D`), transmit `ESC` followed by `ESC` (`[0x7D, 0x7D]`).
3. Any other byte is transmitted unchanged.

```python
def byte_stuff_frame(payload):
    frame = [FLAG]
    for byte in payload:
        if byte == FLAG or byte == ESC:
            frame.append(ESC)
        frame.append(byte)
    frame.append(FLAG)
    return frame
```

#### Receiver Deframing State Machine:
```python
def byte_stuff_deframe(frame):
    if len(frame) < 2:
        return []
    data = frame[1:-1]  # Strip starting and ending FLAGs
    payload = []
    i = 0
    while i < len(data):
        if data[i] == ESC:
            if i + 1 >= len(data):
                raise ValueError("Invalid trailing ESC sequence")
            payload.append(data[i + 1])
            i += 2
        else:
            payload.append(data[i])
            i += 1
    return payload
```

### 4.3 Error Recovery & Resynchronization Boundary
If noise corrupts bytes inside a frame (or even corrupts an `ESC` byte), the receiver may drop or mangle the current frame. However, **as soon as the receiver encounters the next `0x7E` byte, it immediately regains frame boundary synchronization**. Errors never propagate to subsequent frames.

---

## 5. Part C: Bit Stuffing (Bit-Oriented Framing / HDLC)

### 5.1 The Six-Consecutive-Ones Flag (`01111110`)
Bit-oriented framing operates at the individual bit level rather than byte boundaries. A frame begins and ends with the special 8-bit flag sequence:
$$\text{FLAG} = \mathbf{01111110} \quad (\text{a zero, six ones, and a zero})$$

### 5.2 Five-Ones Rule Algorithm & Packing Logic

#### Transmitter Stuffing Rule:
The transmitter scans the bitstream. Whenever it encounters **five consecutive `1` bits**, it unconditionally injects (stuffs) a **`0` bit** into the outgoing stream:

```
Payload bits:   ... 0 1 1 1 1 1 1 0 ...
Stuffed stream: ... 0 1 1 1 1 1 [0] 1 0 ...
```
Because a `0` is inserted after every sequence of five `1`s, the pattern `01111110` (six `1`s) **can never appear inside the transmitted data stream**, guaranteeing total transparency!

#### Receiver Unstuffing Rule:
The receiver examines incoming bits:
- When five consecutive `1`s are received:
  1. If the next bit is `0`: It is a stuffed bit $\implies$ **discard the `0`** and continue.
  2. If the next bit is `1`:
     - If followed by `0` (`01111110`): It is a **FLAG** (frame delimiter).
     - If followed by `1` (`01111111`): It is an **ABORT signal** (transmission cancelled / line idle).

```python
def bit_stuff(payload):
    orig_bits = bytes_to_bits(payload)
    stuffed = []
    ones_count = 0
    for bit in orig_bits:
        stuffed.append(bit)
        if bit == 1:
            ones_count += 1
            if ones_count == 5:
                stuffed.append(0)  # Stuff a 0 bit
                ones_count = 0
        else:
            ones_count = 0
    return pack_bits_into_bytes(stuffed)
```

---

## 6. Part D: Resilience, Transmission Errors & Overhead Analysis

### 6.1 Single-Byte Corruption Simulation
Simulating a transmission medium with single-byte error injection demonstrates the stark difference in error recovery:

| Scenario | Injected Corruption | Byte Count Result | Byte Stuffing Result | Bit Stuffing Result |
| :--- | :--- | :--- | :--- | :--- |
| **Clean Stream** | None | 100% Frames Decoded | 100% Frames Decoded | 100% Frames Decoded |
| **Byte 0 Corrupted** | Length count flipped | **100% Total Stream Failure** | Frame 1 corrupted; Frame 2 recovered | Frame 1 corrupted; Frame 2 recovered |
| **Payload Inversion**| Single data bit flipped | CRC checks fail on Frame 1; Frame 2 OK | CRC checks fail on Frame 1; Frame 2 OK | CRC checks fail on Frame 1; Frame 2 OK |

### 6.2 Framing Overhead & Worst-Case Payload Expansion

1. **Byte Count Overhead:**
   - Fixed: Exactly 1 byte per frame ($1 / N$).
   - Worst case: No expansion ($0\%$).
2. **Byte Stuffing Overhead:**
   - Best case: 2 bytes per frame (Start and End FLAGs).
   - **Worst case:** If a payload consists entirely of `0x7E` and `0x7D` bytes, every byte is doubled by an `ESC` byte $\implies \mathbf{100\% \text{ expansion}}$ ($2N + 2$).
3. **Bit Stuffing Overhead:**
   - Best case: 16 bits (2 flag bytes).
   - **Worst case:** If a payload consists entirely of all `1`s (`0xFF`), one `0` bit is stuffed every 5 bits $\implies \mathbf{20\% \text{ expansion}}$ ($\approx N/5$).

---

## 7. Software Architecture & Python Implementation (`assignment3.py`)

The complete Python script in `LAB3` implements:
- `hex_bytes(data)`: Displays byte streams in formatted hexadecimal.
- `byte_count_frame()` & `byte_count_parse()`: Length-prefix framing.
- `byte_stuff_frame()` & `byte_stuff_deframe()`: Character stuffing with escape sequencing.
- `bytes_to_bits()`, `pack_bits_into_bytes()`, `bit_stuff()`, `bit_destuff()`: Bit-level manipulation, stuffing, and stream deframing.
- Verification tests with error injection.

---

## 8. Comprehensive Viva & Exam Preparation Guide

### Q1: What is the primary disadvantage of the Byte Count framing method?
**Answer:** It lacks resynchronization capability. If a transmission error corrupts the count field, the receiver incorrectly interprets data bytes as future count fields, causing catastrophic, permanent frame desynchronization for the remainder of the transmission.

### Q2: How does Byte Stuffing guarantee transparency when a payload contains a flag byte?
**Answer:** Whenever the sender encounters a `FLAG` (`0x7E`) in the user data, it inserts an `ESC` (`0x7D`) byte immediately before it. The receiver sees the `ESC`, recognizes it as an escape character, removes the `ESC`, and treats the following `FLAG` byte as ordinary user payload data rather than a frame delimiter.

### Q3: What happens if the payload in Byte Stuffing contains an `ESC` byte?
**Answer:** The sender escapes the escape byte by transmitting two consecutive `ESC` bytes (`[0x7D, 0x7D]`). Upon reception, the receiver discards the first `ESC` and retains the second `ESC` as literal data.

### Q4: In Bit Stuffing, why do we stuff a `0` after five consecutive `1`s even if the sixth bit was already a `0`?
**Answer:** To prevent ambiguity. If the transmitter did not stuff a `0` when the sixth bit was already `0`, the receiver would not be able to tell whether a sequence `0111110` in the incoming stream was original user data or a stuffed pattern. By stuffing unconditionally after five `1`s, the receiver knows with absolute certainty that any `0` following five `1`s is a stuffed bit and must be discarded.

### Q5: What is the maximum possible overhead in Bit Stuffing?
**Answer:** In the worst-case scenario where the user payload consists entirely of binary `1`s, a `0` bit is stuffed every 5 bits, resulting in an expansion overhead of $1 / 5 = \mathbf{20\%}$.

### Q6: How does a bit-stuffing receiver detect an aborted transmission?
**Answer:** If the receiver detects **seven or more consecutive `1` bits** (`01111111...`), this violates the protocol rules (as a flag has six `1`s and data never has more than five `1`s). This sequence is defined as an **ABORT pattern**, prompting the receiver to discard the current frame immediately.

---
*End of Lab 3 Report · Prepared for CS353 Computer Networks*

