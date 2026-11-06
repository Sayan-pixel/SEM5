# CS353: Error Detection & Correction (Hamming Codes & CRC)
## Comprehensive Lab Report, Theory Guide & Implementation Manual
**Course:** CS353 · Computer Networks · Week 4 / Lab 4  
**Topic:** Data Link Layer / Error-Control Coding, SEC Hamming Codes & Cyclic Redundancy Check (CRC)  
**System Implemented:** 1-Indexed SEC Hamming Encoder/Decoder and Polynomial Modulo-2 CRC Engine in Python

---

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [Theoretical Foundations of Error Control](#2-theoretical-foundations-of-error-control)
   - [2.1 Error Detection vs. Error Correction](#21-error-detection-vs-error-correction)
   - [2.2 Hamming Distance and Error-Bound Theorems](#22-hamming-distance-and-error-bound-theorems)
3. [Task A: Hamming Single Error Correction (SEC) Codes](#3-task-a-hamming-single-error-correction-sec-codes)
   - [3.1 Redundancy Inequality ($2^r \ge m + r + 1$)](#31-redundancy-inequality-2r-ge-m--r--1)
   - [3.2 1-Indexed Bit Layout & Parity Coverage](#32-1-indexed-bit-layout--parity-coverage)
   - [3.3 Mathematical Encoding Algorithm](#33-mathematical-encoding-algorithm)
   - [3.4 Syndrome Decoding & Automatic Bit Inversion](#34-syndrome-decoding--automatic-bit-inversion)
   - [3.5 Step-by-Step Numerical Walkthrough (`11001010`)](#35-step-by-step-numerical-walkthrough-11001010)
4. [Task B: Cyclic Redundancy Check (CRC) Engine](#4-task-b-cyclic-redundancy-check-crc-engine)
   - [4.1 Polynomial Representation of Bitstrings](#41-polynomial-representation-of-bitstrings)
   - [4.2 Galois Field $\text{GF}(2)$ & Modulo-2 Arithmetic](#42-galois-field-textgf2--modulo-2-arithmetic)
   - [4.3 Sender CRC Remainder Generation ($M(x) \cdot x^k \pmod{G(x)}$)](#43-sender-crc-remainder-generation-mx-cdot-xk-pmodgx)
   - [4.4 Receiver Verification & Syndrome Check](#44-receiver-verification--syndrome-check)
   - [4.5 Step-by-Step Numerical Walkthrough (`1010111` with `1001`)](#45-step-by-step-numerical-walkthrough-1010111-with-1001)
5. [Software Architecture & Implementation (`assignment4.py`)](#5-software-architecture--implementation-assignment4py)
6. [Comprehensive Viva & Exam Preparation Guide (Answering PDF Questions)](#6-comprehensive-viva--exam-preparation-guide-answering-pdf-questions)

---

## 1. Executive Summary

Transmission lines are subject to thermal noise, impulse noise, and electromagnetic interference. As bits travel across the physical medium, signal degradation causes binary bits to invert ($0 \to 1$ or $1 \to 0$).

To maintain data integrity without upper-layer intervention, the Data Link Layer deploys two error-control approaches:
1. **Forward Error Correction (FEC) via Hamming Codes:** The transmitter adds structured redundancy bits allowing the receiver to independently detect **and correct** single-bit errors without requesting retransmission.
2. **Error Detection via Cyclic Redundancy Checks (CRC):** The transmitter appends a short polynomial remainder (FCS). The receiver verifies the polynomial division; any corrupted frame is detected with near-100% certainty and dropped.

---

## 2. Theoretical Foundations of Error Control

### 2.1 Error Detection vs. Error Correction
- **Error Detection:** Adding enough redundancy to identify whether one or more bits were altered during transit. The receiver cannot locate the corrupted bit; it discards the frame and relies on an Automatic Repeat reQuest (ARQ) protocol to retransmit it.
- **Error Correction (FEC):** Adding sufficient structured redundancy to locate the exact coordinate of the corrupted bit and invert it back to its original state. Indispensable for simplex channels (no feedback), satellite links (long RTT), and high-loss environments.

### 2.2 Hamming Distance and Error-Bound Theorems
The **Hamming Distance ($d_H$)** between two codewords is the number of bit positions in which they differ. For a code with minimum Hamming distance $d_{\min}$:
1. **Detection Capability:** To detect up to $e$ bit errors, the minimum distance must satisfy:
   $$d_{\min} \ge e + 1$$
2. **Correction Capability:** To correct up to $t$ bit errors, the minimum distance must satisfy:
   $$d_{\min} \ge 2t + 1$$

> A **Single Error Correcting (SEC)** Hamming code has $d_{\min} = 3$. It can either correct $1$ bit error ($2(1) + 1 = 3$) OR detect up to $2$ bit errors ($2 + 1 = 3$).

---

## 3. Task A: Hamming Single Error Correction (SEC) Codes

### 3.1 Redundancy Inequality ($2^r \ge m + r + 1$)
For an arbitrary message of $m$ data bits, we append $r$ redundant parity bits to form an $n = m + r$ bit codeword.
When the receiver evaluates the $n$-bit codeword, the computed syndrome must be able to represent:
- $n$ distinct single-bit error states (error at bit 1, bit 2, ..., bit $n$).
- $1$ error-free state (syndrome $= 0$).

Since $r$ bits can represent $2^r$ unique values, the fundamental **Hamming Rule** requires:
$$2^r \ge m + r + 1$$

| Data Bits ($m$) | Redundant Bits ($r$) | Codeword Length ($n = m + r$) | Redundancy Ratio ($r / m$) |
| :---: | :---: | :---: | :---: |
| 4 | 3 | 7 (Hamming (7,4)) | 75% |
| **8** | **4** | **12 (Hamming (12,8))** | **50%** |
| 16 | 5 | 21 | 31.25% |
| 32 | 6 | 38 | 18.75% |

---

### 3.2 1-Indexed Bit Layout & Parity Coverage
Hamming codes place parity bits at **power-of-2 positions**:
$$P_k \text{ resides at index } 2^{k-1} \implies \text{Positions } 1, 2, 4, 8, 16, \dots$$
All other positions carry the original data bits ($D_1, D_2, \dots$):

```
Position:  1   2   3   4   5   6   7   8   9  10  11  12
Bit Role: P1  P2  D1  P4  D2  D3  D4  P8  D5  D6  D7  D8
Binary:  0001 0010 0011 0100 0101 0110 0111 1000 1001 1010 1011 1100
```

#### Parity Coverage Rule:
Parity bit $P_{2^k}$ checks all bit positions whose binary representation has the $(k+1)$-th bit set to `1`:
- **$P_1$ (checks least significant bit = 1):** Positions 1, 3, 5, 7, 9, 11, ...
- **$P_2$ (checks second bit = 1):** Positions 2, 3, 6, 7, 10, 11, ...
- **$P_4$ (checks third bit = 1):** Positions 4, 5, 6, 7, 12, ...
- **$P_8$ (checks fourth bit = 1):** Positions 8, 9, 10, 11, 12, ...

---

### 3.3 Mathematical Encoding Algorithm
Under **Even Parity**, each parity bit $P_i$ is chosen such that the total number of `1`s across its covered positions is **even**:

$$P_1 = D_1 \oplus D_2 \oplus D_4 \oplus D_5 \oplus D_7 \dots$$
$$P_2 = D_1 \oplus D_3 \oplus D_4 \oplus D_6 \oplus D_7 \dots$$
$$P_4 = D_2 \oplus D_3 \oplus D_4 \oplus D_8 \dots$$
$$P_8 = D_5 \oplus D_6 \oplus D_7 \oplus D_8 \dots$$

---

### 3.4 Syndrome Decoding & Automatic Bit Inversion
Upon receiving codeword $C'$, the receiver computes the parity check bits $S_1, S_2, S_4, S_8$:
$$S_1 = P_1' \oplus D_1' \oplus D_2' \oplus D_4' \oplus \dots$$
$$S_2 = P_2' \oplus D_1' \oplus D_3' \oplus D_4' \oplus \dots$$
$$S_4 = P_4' \oplus D_2' \oplus D_3' \oplus D_4' \oplus \dots$$
$$S_8 = P_8' \oplus D_5' \oplus D_6' \oplus D_7' \oplus \dots$$

The **Error Syndrome Integer** is formed directly by concatenating:
$$\text{Syndrome} = S_8 S_4 S_2 S_1 \text{ (binary integer)}$$

- If $\text{Syndrome} = 0$: No bit error occurred.
- If $\text{Syndrome} = k \ne 0$: A single-bit error occurred at **exact bit position $k$**!
  The receiver inverts bit $k$:
  $$C'[k] = C'[k] \oplus 1$$
  and extracts the original data bits!

---

### 3.5 Step-by-Step Numerical Walkthrough (`11001010`)

#### 1. Input Data:
$$m = 8 \text{ bits}: \mathbf{11001010} \quad (D_1=1, D_2=1, D_3=0, D_4=0, D_5=1, D_6=0, D_7=1, D_8=0)$$
$$2^r \ge 8 + r + 1 \implies r = 4 \implies n = 12\text{ bits}$$

#### 2. Position Allocation:
```
Pos:   1   2   3   4   5   6   7   8   9  10  11  12
Role: P1  P2  D1  P4  D2  D3  D4  P8  D5  D6  D7  D8
Bits:  ?   ?   1   ?   1   0   0   ?   1   0   1   0
```

#### 3. Compute Even Parities:
- $P_1$: positions $3(1), 5(1), 7(0), 9(1), 11(1) \implies \text{Sum of 1s} = 4$ (even) $\implies \mathbf{P_1 = 0}$
- $P_2$: positions $3(1), 6(0), 7(0), 10(0), 11(1) \implies \text{Sum of 1s} = 2$ (even) $\implies \mathbf{P_2 = 0}$
- $P_4$: positions $5(1), 6(0), 7(0), 12(0) \implies \text{Sum of 1s} = 1$ (odd) $\implies \mathbf{P_4 = 1}$
- $P_8$: positions $9(1), 10(0), 11(1), 12(0) \implies \text{Sum of 1s} = 2$ (even) $\implies \mathbf{P_8 = 0}$

**Encoded 12-bit Codeword:**
$$\mathbf{001110001010}$$

#### 4. Error Injection & Syndrome Correction:
Flip bit at position 7 ($0 \to 1$):
$$\text{Received Codeword} = \mathbf{001110101010}$$
- $S_1 = \text{bits}(1,3,5,7,9,11) = 0 \oplus 1 \oplus 1 \oplus 1 \oplus 1 \oplus 1 = \mathbf{1}$
- $S_2 = \text{bits}(2,3,6,7,10,11) = 0 \oplus 1 \oplus 0 \oplus 1 \oplus 0 \oplus 1 = \mathbf{1}$
- $S_4 = \text{bits}(4,5,6,7,12) = 1 \oplus 1 \oplus 0 \oplus 1 \oplus 0 = \mathbf{1}$
- $S_8 = \text{bits}(8,9,10,11,12) = 0 \oplus 1 \oplus 0 \oplus 1 \oplus 0 = \mathbf{0}$

$$\text{Syndrome} = (S_8, S_4, S_2, S_1)_2 = (0111)_2 = \mathbf{7}$$
Bit 7 is inverted from $1 \to 0$. Recovered codeword $= \mathbf{001110001010}$, original data $= \mathbf{11001010}$. **Successfully corrected!**

---

## 4. Task B: Cyclic Redundancy Check (CRC) Engine

### 4.1 Polynomial Representation of Bitstrings
A $k$-bit binary string is treated as the coefficients of a polynomial in Galois Field $\text{GF}(2)$:
$$\text{Bitstring } 10011 \iff P(x) = 1 \cdot x^4 + 0 \cdot x^3 + 0 \cdot x^2 + 1 \cdot x^1 + 1 \cdot x^0 = x^4 + x + 1$$

### 4.2 Galois Field $\text{GF}(2)$ & Modulo-2 Arithmetic
In $\text{GF}(2)$ polynomial arithmetic:
- **Addition and Subtraction are IDENTICAL** and equal to bitwise **XOR ($\oplus$)**.
- There are **no carries in addition** and **no borrows in subtraction**:
  $$0 \oplus 0 = 0, \quad 0 \oplus 1 = 1, \quad 1 \oplus 0 = 1, \quad 1 \oplus 1 = 0$$

### 4.3 Sender CRC Remainder Generation ($M(x) \cdot x^k \pmod{G(x)}$)
Let $M(x)$ be an $m$-bit message, and $G(x)$ be a generator polynomial of degree $k$ ($k+1$ bits).
1. Append $k$ zeros to the end of the message: $M'(x) = M(x) \cdot x^k$.
2. Divide $M'(x)$ by $G(x)$ using modulo-2 long division (XOR).
3. The division yields a quotient $Q(x)$ and a $k$-bit remainder $R(x)$:
   $$M(x) \cdot x^k = Q(x) \cdot G(x) \oplus R(x)$$
4. Append remainder $R(x)$ to the original message:
   $$T(x) = M(x) \cdot x^k \oplus R(x)$$
   By construction, $T(x)$ is **strictly divisible by $G(x)$** with zero remainder.

### 4.4 Receiver Verification & Syndrome Check
The receiver receives frame $T'(x) = T(x) \oplus E(x)$, where $E(x)$ represents transmission errors.
The receiver divides $T'(x)$ by $G(x)$:
$$\frac{T'(x)}{G(x)} = \frac{T(x) \oplus E(x)}{G(x)} = Q(x) \oplus \frac{E(x)}{G(x)}$$
- If remainder $= 0$: Frame is accepted (no detected error).
- If remainder $\ne 0$: Frame is rejected.

---

### 4.5 Step-by-Step Numerical Walkthrough (`1010111` with `1001`)

- Message: `1010111` ($m = 7$)
- Generator: `1001` ($x^3 + 1$, degree $k = 3$)
- Message with 3 zeros appended: `1010111000`

#### Modulo-2 Long Division:
```
            1011011 (Quotient)
     -------------------
1001 | 1010111000
       1001
       ----
        0111
        0000
        ----
         1111
         1001
         ----
          1101
          1001
          ----
           1000
           0000
           ----
            1000
            1001
            ----
             0010
             0000
             ----
              0100  <--- Remainder R = 100 (3 bits)
```

- Remainder: `100`
- Transmitted Frame: `1010111` + `100` = $\mathbf{1010111100}$

#### Receiver Check on Clean Frame:
Dividing `1010111100` by `1001` yields remainder $\mathbf{000} \implies$ **ACCEPT**.

#### Receiver Check on Corrupted Frame:
Flip bit 4 from right (`1010111100` $\to$ `1010110100`):
Dividing `1010110100` by `1001` yields remainder $\mathbf{010} \ne 000 \implies$ **REJECT**.

---

## 5. Software Architecture & Implementation (`assignment4.py`)

The Python implementation in `LAB4` provides:
- `calculate_redundant_bits(m)`: Solves $2^r \ge m + r + 1$.
- `hamming_encode(data_bits)`: Constructs 1-indexed SEC codeword.
- `hamming_decode(codeword)`: Reconstructs syndrome and corrects single-bit error.
- `crc_encode(message_bits, generator_bits)`: Modulo-2 binary long division.
- `crc_check(received_bits, generator_bits)`: Verifies polynomial divisibility.

---

## 6. Comprehensive Viva & Exam Preparation Guide (Answering PDF Questions)

### Q1: If two valid Hamming codewords differ in exactly 3 bit positions, and a codeword suffers 2 bit errors, will the SEC Hamming decoder always detect that something is wrong? Will it always correct it correctly? Explain.
**Answer:**
1. **Will it detect that something is wrong?** **YES.** Because the minimum Hamming distance is $d_{\min} = 3$, any 2-bit error produces a bit pattern that is NOT a valid codeword. The computed syndrome will be non-zero, signaling an error.
2. **Will it correct it correctly?** **NO.** An SEC Hamming code can only correct $t = \lfloor (d_{\min} - 1) / 2 \rfloor = 1$ bit error. If 2 bits flip, the received pattern is distance 2 from the original codeword, but distance **1** from some *other* valid codeword! The decoder assumes only a single bit flipped, points to that nearest false codeword, and inverts a 3rd bit—corrupting the data further. To detect double errors without miscorrecting, a **Single Error Correcting, Double Error Detecting (SEC-DED)** code with an extra overall parity bit ($d_{\min} = 4$) is required.

### Q2: What is the maximum number of data bits that can be protected by an SEC Hamming code using 4 parity bits? Using 5 parity bits?
**Answer:**
Using the inequality $2^r \ge m + r + 1 \iff m \le 2^r - r - 1$:
- **For $r = 4$ parity bits:**
  $$m \le 2^4 - 4 - 1 = 16 - 5 = \mathbf{11\text{ data bits}}$$
  (Total codeword length $n = 15$).
- **For $r = 5$ parity bits:**
  $$m \le 2^5 - 5 - 1 = 32 - 6 = \mathbf{26\text{ data bits}}$$
  (Total codeword length $n = 31$).

### Q3: Why does modulo-2 (XOR) division use no borrow or carry, unlike ordinary binary division?
**Answer:**
Ordinary arithmetic operates over the infinite ring of integers $\mathbb{Z}$, where numbers have magnitude and place values depend on adjacent powers. Modulo-2 arithmetic operates over the **finite field $\text{GF}(2)$**, where operations are performed on polynomial coefficients independently. In $\text{GF}(2)$, $1 + 1 = 0$ (no carry) and $0 - 1 = 1$ (no borrow). Addition and subtraction are both identical to the bitwise exclusive-OR (XOR) operation.

### Q4: Give an example of an error pattern that CRC with a given generator polynomial $G(x)$ would fail to detect. Under what condition does this happen?
**Answer:**
Let the transmitted codeword polynomial be $T(x)$, and the received polynomial be $T'(x) = T(x) \oplus E(x)$, where $E(x)$ is the error polynomial (having `1`s at corrupted positions).
The receiver checks $\frac{T'(x)}{G(x)} = \frac{T(x)}{G(x)} \oplus \frac{E(x)}{G(x)}$. Since $T(x)$ is divisible by $G(x)$, the remainder is determined entirely by $\frac{E(x)}{G(x)}$.
- **Failure Condition:** CRC fails to detect an error **if and only if the error polynomial $E(x)$ is an exact multiple of the generator polynomial $G(x)$** (i.e. $E(x) = Q(x) \cdot G(x)$).
- **Example:** If $G(x) = x^3 + 1$ (`1001`), and noise flips the bits corresponding exactly to $E(x) = x^3 + 1$ (bits at distance 3), then $E(x) / G(x) = 1$ with **zero remainder**. The receiver accepts the corrupted frame as valid.

### Q5: Compare the redundancy overhead of Hamming code and CRC-32 for a 1000-bit data frame. Which is more bit-efficient, and why is CRC still preferred on most networks despite not correcting errors?
**Answer:**
1. **Hamming Code Overhead for $m = 1000\text{ bits}$:**
   $2^r \ge 1000 + r + 1 \implies r = 10$ parity bits.
   Redundancy overhead $= 10\text{ bits}$.
2. **CRC-32 Overhead:**
   Regardless of frame length, CRC-32 appends exactly 32 bits of FCS.
   Redundancy overhead $= 32\text{ bits}$.
3. **Why CRC is Preferred over Hamming Codes on Networks:**
   - **Bursty Noise Realities:** Noise on computer networks (lightning, electrical switches, crosstalk) occurs in **bursts**, corrupting dozens of consecutive bits. A Hamming code completely fails on burst errors larger than 1 bit. In contrast, CRC-32 detects **all burst errors of length $\le 32$ bits**, and $> 99.9999997\%$ of longer bursts!
   - **Retransmission is Cheap:** On modern high-speed networks, bit error rates are very low ($< 10^{-9}$). It is far more efficient to send 32 check bits, detect errors with near-perfection, and retransmit the rare bad packet via ARQ, rather than wasting complex FEC decoding hardware on every single frame.

### Q6: Briefly describe how a CRC could be computed in hardware using a Linear Feedback Shift Register (LFSR).
**Answer:**
In hardware, CRC is implemented with an $r$-stage shift register containing $r$ flip-flops connected by XOR gates:
1. The shift register is initialized to zero.
2. The message bits are shifted in serially, one bit per clock cycle, from highest degree to lowest degree.
3. The XOR gates are placed at the feedback taps corresponding to the terms of the generator polynomial $G(x)$ where coefficients are `1`.
4. As each bit enters, if the high-order bit exiting the register is `1`, the register contents are XORed with $G(x)$ in parallel during that clock cycle.
5. After all message bits have shifted through, the final values remaining in the $r$ flip-flops are the exact **CRC remainder**, computed in $O(1)$ hardware time per bit without any CPU division cycles.

---
*End of Lab 4 Report · Prepared for CS353 Computer Networks*

