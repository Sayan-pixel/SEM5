# CS353: Characterising the Physical Channel
## Comprehensive Lab Report, Theory Guide & Implementation Manual
**Course:** CS353 · Computer Networks · Week 2 / Lab 2  
**Topic:** Physical Layer / Transmission Media, Channel Capacity, Attenuation & Bit Error Rates  
**System Analyzed:** Copper Twisted-Pair (Cat5e, Cat6, Cat6a), Optical Fibre, Wireless Propagation (Friis Model), and BPSK Modulation

---

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [Theoretical Foundations of the Physical Layer](#2-theoretical-foundations-of-the-physical-layer)
   - [2.1 Signals, Bandwidth, and Transmission Media](#21-signals-bandwidth-and-transmission-media)
   - [2.2 Nyquist Formulation for Noiseless Channels](#22-nyquist-formulation-for-noiseless-channels)
   - [2.3 Shannon-Hartley Theorem for Noisy Channels](#23-shannon-hartley-theorem-for-noisy-channels)
   - [2.4 Decibels (dB, dBm) and Signal-to-Noise Ratio (SNR)](#24-decibels-db-dbm-and-signal-to-noise-ratio-snr)
3. [Part A: Bandwidth to Bit Rate Analysis](#3-part-a-bandwidth-to-bit-rate-analysis)
   - [3.1 Cable Specifications & Nyquist Levels Derivation](#31-cable-specifications--nyquist-levels-derivation)
   - [3.2 Shannon Capacity Calculations](#32-shannon-capacity-calculations)
   - [3.3 The Three Ceilings: Nyquist vs. Shannon vs. Hardware](#33-the-three-ceilings-nyquist-vs-shannon-vs-hardware)
4. [Part B: Attenuation, Link Budget & The 100m Ethernet Origin](#4-part-b-attenuation-link-budget--the-100m-ethernet-origin)
   - [4.1 Logarithmic Power Attenuation Model](#41-logarithmic-power-attenuation-model)
   - [4.2 Copper vs. Optical Fibre Reach Comparison](#42-copper-vs-optical-fibre-reach-comparison)
   - [4.3 Derivation of the 100 m Ethernet Limit](#43-derivation-of-the-100-m-ethernet-limit)
5. [Part C: Wireless Free-Space Path Loss (Friis Model)](#5-part-c-wireless-free-space-path-loss-friis-model)
   - [5.1 The Friis Transmission Equation](#51-the-friis-transmission-equation)
   - [5.2 Path Loss Across 900 MHz, 2.4 GHz, and 5 GHz](#52-path-loss-across-900-mhz-24-ghz-and-5-ghz)
   - [5.3 Why Higher Frequencies Suffer Greater Attenuation](#53-why-higher-frequencies-suffer-greater-attenuation)
6. [Part D: Bit Error Rate (BER) & Channel Reliability](#6-part-d-bit-error-rate-ber--channel-reliability)
   - [6.1 Channel SNR vs. Energy-per-Bit Ratio ($E_b/N_0$)](#61-channel-snr-vs-energy-per-bit-ratio-ebn0)
   - [6.2 BPSK Error Probability Formulation](#62-bpsk-error-probability-formulation)
   - [6.3 Identifying the $10^{-3}$ BER Threshold](#63-identifying-the-10-3-ber-threshold)
   - [6.4 One-Line Channel Quality Summary](#64-one-line-channel-quality-summary)
7. [Software Architecture & Python Implementation](#7-software-architecture--python-implementation)
   - [7.1 Complete Code Walkthrough (`lab2_template.py`)](#71-complete-code-walkthrough-lab2_templatepy)
   - [7.2 Generated Plots & Visualizations](#72-generated-plots--visualizations)
8. [Comprehensive Viva & Exam Preparation Guide](#8-comprehensive-viva--exam-preparation-guide)

---

## 1. Executive Summary

The Physical Layer is tasked with moving raw binary digits (bits) across physical transmission media. The maximum data rate, propagation distance, and reliability of any physical channel are strictly governed by electromagnetic laws, information theory, and thermodynamics.

In Lab 2, we perform a complete mathematical and empirical characterization of four communication media:
1. **Copper Twisted-Pair Cables (Cat5e, Cat6, Cat6a):** Evaluating modulation complexity via Nyquist and ultimate data capacity via Shannon.
2. **Optical Fibre:** Demonstrating why light pulses over silica glass achieve orders-of-magnitude greater distances than copper conductors.
3. **The 100 m Copper Ethernet Limit:** Analytically deriving the universal $100\text{ m}$ distance boundary from high-frequency attenuation ($\alpha = 220\text{ dB/km}$) and LAN receiver sensitivity ($22\text{ dB}$).
4. **Wireless Radio Links:** Quantifying Free-Space Path Loss (FSPL) using the Friis equation across $900\text{ MHz}$, $2.4\text{ GHz}$, and $5\text{ GHz}$.
5. **Bit Error Rate (BER):** Calculating transmission error probability using the complementary error function ($\operatorname{erfc}$) for Binary Phase Shift Keying (BPSK).

---

## 2. Theoretical Foundations of the Physical Layer

### 2.1 Signals, Bandwidth, and Transmission Media
Any real-world transmission channel acts as a **band-pass or low-pass filter**. Fourier analysis proves that any periodic or arbitrary signal consists of a sum of sinusoidal harmonics at different frequencies:
- **Bandwidth ($B$):** The range of frequencies (measured in Hertz, Hz) that the medium can pass without excessive signal attenuation.
- **Baud Rate (Symbol Rate, $S$):** The number of signal state transitions (symbols) transmitted per second.
- **Bit Rate ($R$):** The number of actual information bits transmitted per second ($R = S \times \text{bits per symbol}$).

### 2.2 Nyquist Formulation for Noiseless Channels
In 1928, Harry Nyquist proved that if an arbitrary signal is passed through a low-pass filter of bandwidth $B$, the signal can be completely reconstructed by taking $2B$ independent samples per second. Therefore, the maximum baud rate over a noiseless channel is:

$$\text{Baud Rate}_{\max} = 2B \text{ symbols/sec}$$

If each signal symbol is chosen from an alphabet of $M$ discrete discrete voltage or phase levels, each symbol carries:
$$\text{Bits per symbol} = \log_2(M)$$

Thus, the **Nyquist Maximum Bit Rate** for a noiseless channel is:
$$C_{\text{Nyquist}} = 2B \log_2(M) \text{ bps}$$

Inverting this formula allows an engineer to determine how many discrete signal levels $M$ are required to achieve a target bit rate $R$:
$$M = 2^{R / (2B)}$$

### 2.3 Shannon-Hartley Theorem for Noisy Channels
In 1948, Claude Shannon extended channel capacity theory to real-world channels corrupted by **Additive White Gaussian Noise (AWGN)**. Regardless of how many signal levels $M$ or what modulation scheme is employed, thermal noise imposes an absolute upper bound on error-free data throughput:

$$C_{\text{Shannon}} = B \log_2\left(1 + \frac{S}{N}\right) \text{ bps}$$

where:
- $B$ is the channel bandwidth in Hertz.
- $S/N$ is the **linear Signal-to-Noise Ratio** (dimensionless power ratio).

### 2.4 Decibels (dB, dBm) and Signal-to-Noise Ratio (SNR)
Signal and noise powers vary over dozens of orders of magnitude, making logarithmic decibel scales essential:

$$\text{SNR}_{\text{dB}} = 10 \log_{10}\left(\frac{S}{N}\right) \iff \frac{S}{N} = 10^{\text{SNR}_{\text{dB}} / 10}$$

For absolute power referenced to $1\text{ milliwatt}$ ($1\text{ mW}$):
$$P_{\text{dBm}} = 10 \log_{10}\left(\frac{P_{\text{mW}}}{1\text{ mW}}\right)$$

- $0\text{ dBm} = 1\text{ mW}$
- $-40\text{ dBm} = 10^{-4}\text{ mW} = 0.1\text{ }\mu\text{W}$

---

## 3. Part A: Bandwidth to Bit Rate Analysis

### 3.1 Cable Specifications & Nyquist Levels Derivation
We examine three standard Ethernet copper cable grades tasked with achieving a target throughput of $R = 1\text{ Gbps} = 10^9\text{ bps}$:

| Cable Grade | Specified Bandwidth ($B$) | Required Nyquist Levels ($M = 2^{R / 2B}$) | Evaluation | Bits/Symbol ($\log_2 M$) |
| :--- | :--- | :--- | :--- | :--- |
| **Cat5e** | $100\text{ MHz} = 10^8\text{ Hz}$ | $M = 2^{10^9 / (2 \times 10^8)} = 2^5$ | $\mathbf{M = 32}$ | $5\text{ bits/symbol}$ |
| **Cat6** | $250\text{ MHz} = 2.5 \times 10^8\text{ Hz}$ | $M = 2^{10^9 / (2 \times 2.5 \times 10^8)} = 2^2$ | $\mathbf{M = 4}$ | $2\text{ bits/symbol}$ |
| **Cat6a** | $500\text{ MHz} = 5 \times 10^8\text{ Hz}$ | $M = 2^{10^9 / (2 \times 5 \times 10^8)} = 2^1$ | $\mathbf{M = 2}$ | $1\text{ bit/symbol}$ |

#### Fundamental Engineering Relationship:
> **Core Law:** As the physical bandwidth of the transmission medium increases, the number of distinct signal levels required to sustain the same bit rate decreases exponentially. 
> - Cat6a requires only a binary scheme ($M=2$, e.g. $+V$ and $-V$).
> - Cat5e requires a complex 32-level constellation ($M=32$), making it significantly more sensitive to noise.

---

### 3.2 Shannon Capacity Calculations
For a channel with $\text{SNR} = 25\text{ dB}$:
$$\frac{S}{N} = 10^{25 / 10} = 10^{2.5} \approx 316.2278$$

The spectral efficiency in bits per second per Hertz is:
$$\eta = \log_2(1 + 316.2278) = \log_2(317.2278) = \frac{\ln(317.2278)}{\ln(2)} \approx 8.3094\text{ bps/Hz}$$

Calculating the theoretical capacity ceiling for each cable grade:

$$\begin{aligned}
C_{\text{Cat5e}} &= 100\text{ MHz} \times 8.3094\text{ bps/Hz} \approx \mathbf{830.94\text{ Mbps}} \\
C_{\text{Cat6}} &= 250\text{ MHz} \times 8.3094\text{ bps/Hz} \approx \mathbf{2077.35\text{ Mbps}} = \mathbf{2.077\text{ Gbps}} \\
C_{\text{Cat6a}} &= 500\text{ MHz} \times 8.3094\text{ bps/Hz} \approx \mathbf{4154.70\text{ Mbps}} = \mathbf{4.155\text{ Gbps}}
\end{aligned}$$

---

### 3.3 The Three Ceilings: Nyquist vs. Shannon vs. Hardware

```
  Data Rate
     ▲
     │  [ Nyquist Ceiling: Fantasy / Noise-Free ]  (Arbitrarily high by setting M -> infinity)
     │   ▲
     │   │
     │  [ Shannon Capacity Ceiling: Physical Truth ] (C = B * log2(1 + S/N))
     │   ▲
     │   │
     │  [ Practical Hardware Operating Region ]     (10-30% below Shannon due to coding loss)
     │   │
  ───┴───┴──────────────────────────────────────────► Time / Technology
```

1. **The Fantasy Ceiling (Nyquist):** Nyquist's formula suggests that by increasing the number of voltage levels $M$, one can transmit infinite data over finite bandwidth. In the real world, this is a fantasy: as $M$ increases, the voltage difference between adjacent levels shrinks, causing noise to corrupt the signal.
2. **The Real Ceiling (Shannon):** Shannon's capacity accounts for thermal noise. It represents the strict physical boundary established by information theory; no modulation or coding algorithm can ever exceed this ceiling without bit errors.
3. **Actual Hardware Performance:** Commercial transceivers operate **strictly below** the Shannon limit (typically reaching 70% to 85% of Shannon capacity). Practical impairments—including inter-symbol interference (ISI), non-ideal pulse shaping, clock jitter, and finite-length forward error correction (FEC)—prevent real hardware from reaching the exact theoretical asymptote.

---

## 4. Part B: Attenuation, Link Budget & The 100m Ethernet Origin

### 4.1 Logarithmic Power Attenuation Model
As an electromagnetic or optical signal travels along a guided medium, its power drops exponentially due to resistive dissipation, dielectric absorption, and radiation loss. In logarithmic decibel notation, attenuation is linear with distance:

$$P(d) = P_{\text{tx}} - \alpha \cdot d$$

where:
- $P_{\text{tx}}$ is transmitter launch power in $\text{dBm}$.
- $\alpha$ is the attenuation coefficient in $\text{dB/km}$.
- $d$ is distance in kilometres.

#### The Link Budget:
The **Link Budget** represents the maximum tolerable signal loss before the received power drops below the receiver's detection threshold (receiver sensitivity, $P_{\text{sens}}$):

$$\text{Link Budget} = P_{\text{tx}} - P_{\text{sens}}$$

Given $P_{\text{tx}} = 0\text{ dBm}$ and $P_{\text{sens}} = -40\text{ dBm}$:
$$\text{Link Budget} = 0 - (-40) = \mathbf{40\text{ dB}}$$

Setting $P(d) = P_{\text{sens}}$ gives the maximum achievable unamplified transmission span:
$$d_{\max} = \frac{P_{\text{tx}} - P_{\text{sens}}}{\alpha} = \frac{\text{Link Budget}}{\alpha}$$

---

### 4.2 Copper vs. Optical Fibre Reach Comparison

#### 1. Long-Haul Copper Cable ($\alpha = 8.0\text{ dB/km}$):
$$d_{\max, \text{copper}} = \frac{40\text{ dB}}{8.0\text{ dB/km}} = \mathbf{5.0\text{ km}}$$

#### 2. Single-Mode Optical Fibre ($\alpha = 0.3\text{ dB/km}$ at $1550\text{ nm}$):
$$d_{\max, \text{fibre}} = \frac{40\text{ dB}}{0.3\text{ dB/km}} = \frac{400}{3} \approx \mathbf{133.33\text{ km}}$$

#### Relative Reach Multiplier:
$$\text{Multiplier} = \frac{133.33\text{ km}}{5.0\text{ km}} \approx \mathbf{26.67\times}$$
Optical fibre transmits **over 26 times farther** than copper before requiring signal regeneration.

#### Why Real-World Fibre Reaches Even Further:
1. **Erbium-Doped Fibre Amplifiers (EDFAs):** Long-haul submarine and terrestrial fibre links deploy in-line all-optical amplifiers every 80 km that amplify the optical photons directly without electronic conversion, enabling spans exceeding 10,000 km.
2. **Coherent Optical Receivers:** Advanced coherent detection with digital signal processing (DSP) pushes optical receiver sensitivity below $-45\text{ dBm}$, expanding the link budget.

---

### 4.3 Derivation of the 100 m Ethernet Limit

#### The Physical Mystery:
Why does high-speed copper Ethernet (100Base-TX, 1000Base-T) specify an absolute maximum cable length of exactly **$100\text{ metres}$**?

#### The Mathematical Derivation:
When a Cat5e cable operates at high frequencies ($100\text{ MHz}$), attenuation escalates dramatically due to two high-frequency electromagnetic phenomena:
1. **The Skin Effect:** High-frequency alternating currents travel only on the outer perimeter of the copper conductor, drastically reducing effective cross-sectional area and increasing AC resistance.
2. **Dielectric Loss:** The insulating plastic jacket absorbs high-frequency electromagnetic field energy.

Consequently, at $100\text{ MHz}$, attenuation rises from $8\text{ dB/km}$ to:
$$\alpha_{\text{Cat5e@100MHz}} = \mathbf{220.0\text{ dB/km}}$$

At the same time, commercial Ethernet transceivers require a higher Signal-to-Noise Ratio to decode 100 Mbps / 1 Gbps signals, reducing the allowable LAN link budget to:
$$\text{LAN Link Budget} = \mathbf{22.0\text{ dB}}$$

Computing maximum cable distance:
$$d_{\max} = \frac{\text{LAN Link Budget}}{\alpha} = \frac{22.0\text{ dB}}{220.0\text{ dB/km}} = 0.1\text{ km} = \mathbf{100\text{ metres}}$$

> **Conclusion:** The $100\text{ m}$ Ethernet limit is not an arbitrary standard; it is the exact physical distance where high-frequency skin effect attenuation consumes the transceiver's link budget.

---

## 5. Part C: Wireless Free-Space Path Loss (Friis Model)

### 5.1 The Friis Transmission Equation
Unlike guided media, radio waves radiate outward spherically into free space. The power density decreases with the square of the distance (inverse-square law). The **Free-Space Path Loss (FSPL)** is given in decibels by the Friis equation:

$$\text{FSPL(dB)} = 20\log_{10}(d) + 20\log_{10}(f) + 20\log_{10}\left(\frac{4\pi}{c}\right)$$

where:
- $d$ is distance in metres.
- $f$ is carrier frequency in Hertz.
- $c$ is the speed of light ($3 \times 10^8\text{ m/s}$).

The constant term evaluates to:
$$20\log_{10}\left(\frac{4\pi}{3 \times 10^8}\right) = 20\log_{10}(4.18879 \times 10^{-8}) \approx \mathbf{-147.55\text{ dB}}$$

Received power with $P_{\text{tx}} = 0\text{ dBm}$ is:
$$P_{\text{rx}} = P_{\text{tx}} - \text{FSPL} = -\text{FSPL}$$

---

### 5.2 Path Loss Across 900 MHz, 2.4 GHz, and 5 GHz
Evaluating path loss at a distance of $d = 5\text{ km} = 5000\text{ m}$:

$$\begin{aligned}
20\log_{10}(5000) &= 20 \times 3.69897 = 73.98\text{ dB} \\
\text{FSPL}(d, f) &= 73.98 + 20\log_{10}(f) - 147.55 = 20\log_{10}(f) - 73.57\text{ dB}
\end{aligned}$$

| Frequency Band | Frequency ($f$) | $20\log_{10}(f)$ | FSPL at 5 km | Received Power ($P_{\text{rx}} = 0 - \text{FSPL}$) |
| :--- | :--- | :--- | :--- | :--- |
| **900 MHz** (Sub-1 GHz) | $9 \times 10^8\text{ Hz}$ | $179.08\text{ dB}$ | $\mathbf{105.51\text{ dB}}$ | $\mathbf{-105.51\text{ dBm}}$ |
| **2.4 GHz** (Wi-Fi 4 / BLE) | $2.4 \times 10^9\text{ Hz}$ | $187.60\text{ dB}$ | $\mathbf{114.03\text{ dB}}$ | $\mathbf{-114.03\text{ dBm}}$ |
| **5.0 GHz** (Wi-Fi 5 / 6) | $5.0 \times 10^9\text{ Hz}$ | $193.98\text{ dB}$ | $\mathbf{120.41\text{ dB}}$ | $\mathbf{-120.41\text{ dBm}}$ |

---

### 5.3 Why Higher Frequencies Suffer Greater Attenuation

#### 1. Difference Between 900 MHz and 5 GHz:
$$\Delta P = \text{FSPL}_{5\text{GHz}} - \text{FSPL}_{900\text{MHz}} = 120.41 - 105.51 = \mathbf{14.90\text{ dB}} \approx \mathbf{15\text{ dB}}$$

#### 2. Responsible Term in the Friis Equation:
The exact term responsible for this penalty is:
$$20\log_{10}(f)$$
Taking the ratio of the two frequencies:
$$20\log_{10}\left(\frac{5000\text{ MHz}}{900\text{ MHz}}\right) = 20\log_{10}(5.555) \approx \mathbf{14.89\text{ dB}}$$

#### 3. Physical Intuition (Antenna Effective Aperture):
Higher frequency electromagnetic waves have shorter wavelengths ($\lambda = c/f$). An isotropic receiving antenna has an effective capture area (aperture) proportional to $\lambda^2$:
$$A_e = \frac{\lambda^2}{4\pi} = \frac{c^2}{4\pi f^2}$$
As frequency increases, the antenna aperture physically captures a smaller fraction of the expanding spherical wavefront. Hence, 5 GHz Wi-Fi signals attenuate much faster through space and walls than 900 MHz or 2.4 GHz signals.

---

## 6. Part D: Bit Error Rate (BER) & Channel Reliability

### 6.1 Channel SNR vs. Energy-per-Bit Ratio ($E_b/N_0$)
A common point of confusion in digital communications is distinguishing between **channel SNR** and **energy-per-bit to noise density ($E_b/N_0$)**:
- **Channel SNR ($S/N$):** Ratio of total signal power to total noise power across the entire channel bandwidth $B$. It governs the **maximum information capacity** via Shannon's law.
- **$E_b/N_0$ (Normalized SNR per bit):** Ratio of energy contained within a single bit ($E_b$) to the noise spectral power density ($N_0$, watts per Hz). It directly governs **bit error probability**:
  $$\frac{E_b}{N_0} = \frac{S / R}{N / B} = \left(\frac{S}{N}\right) \times \left(\frac{B}{R}\right)$$

---

### 6.2 BPSK Error Probability Formulation
For Binary Phase Shift Keying (BPSK) over an AWGN channel, the Bit Error Rate (BER) is given by:

$$\text{BER} = \frac{1}{2} \operatorname{erfc}\left(\sqrt{\frac{E_b}{N_0}_{\text{linear}}}\right)$$

where:
- $\frac{E_b}{N_0}_{\text{linear}} = 10^{(E_b/N_0)_{\text{dB}} / 10}$
- $\operatorname{erfc}(x)$ is the complementary error function:
  $$\operatorname{erfc}(x) = \frac{2}{\sqrt{\pi}} \int_x^{\infty} e^{-t^2} dt$$

---

### 6.3 Identifying the $10^{-3}$ BER Threshold
In voice communications and standard packet networks, a raw physical layer BER of $10^{-3}$ ($1$ corrupted bit in $1000$) is a common baseline:

$$\text{BER} = 0.5 \operatorname{erfc}(\sqrt{x}) = 10^{-3} \implies \operatorname{erfc}(\sqrt{x}) = 0.002$$

Inverting the complementary error function:
$$\sqrt{x} \approx 2.185 \implies x = \frac{E_b}{N_0}_{\text{linear}} \approx (2.185)^2 \approx 4.774$$

Converting to decibels:
$$\left(\frac{E_b}{N_0}\right)_{\text{dB}} = 10\log_{10}(4.774) \approx \mathbf{6.79\text{ dB}} \approx \mathbf{6.8\text{ dB}}$$

This confirms the theoretical value required by the lab.

---

### 6.4 One-Line Channel Quality Summary
At an operational target of $E_b/N_0 = 7.0\text{ dB}$:
$$\frac{E_b}{N_0}_{\text{linear}} = 10^{0.7} \approx 5.01187 \implies \sqrt{5.01187} \approx 2.2387$$
$$\text{BER} = 0.5 \operatorname{erfc}(2.2387) \approx \mathbf{7.73 \times 10^{-4}} \approx \mathbf{8 \times 10^{-4}}$$

> **Official One-Line Summary:**  
> *"A Cat5e copper channel over a maximum unamplified span of 5.0 km, with a Shannon capacity ceiling of 831 Mbps at 25 dB SNR, operating at an Eb/N0 of 7.0 dB achieves a bit error rate (BER) of approximately 8 × 10^-4."*

---

## 7. Software Architecture & Python Implementation

### 7.1 Complete Code Walkthrough (`lab2_template.py`)

```python
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

C_LIGHT = 3e8
TX_DBM, RX_SENS_DBM = 0.0, -40.0
SNR_DB = 25
CU_ALPHA, FI_ALPHA = 8.0, 0.3
CAT5E_ALPHA_100MHZ, LAN_BUDGET_DB = 220.0, 22.0

CABLES = [("Cat5e", 100e6), ("Cat6", 250e6), ("Cat6a", 500e6)]
BANDS = [900e6, 2400e6, 5000e6]

def snr_db_to_linear(snr_db):
    """Convert dB to linear power ratio."""
    return 10.0 ** (snr_db / 10.0)

def levels_for_rate(B, target_rate):
    """Part A: Invert Nyquist formula C = 2B log2(M) -> M = 2^(C / 2B)."""
    return int(round(2.0 ** (target_rate / (2.0 * B))))

def shannon_capacity_db(B, snr_db):
    """Part A: Compute Shannon capacity C = B * log2(1 + S/N)."""
    snr_lin = snr_db_to_linear(snr_db)
    return B * math.log2(1.0 + snr_lin)

def max_span_km(tx_dbm, rx_sens_dbm, alpha_db_km):
    """Part B: Compute maximum distance before hitting receiver sensitivity."""
    return (tx_dbm - rx_sens_dbm) / alpha_db_km

def fspl_db(d_m, f_hz):
    """Part C: Free-Space Path Loss using Friis equation."""
    return 20.0 * math.log10(d_m) + 20.0 * math.log10(f_hz) + 20.0 * math.log10(4.0 * math.pi / C_LIGHT)

def ber_bpsk(ebn0_db):
    """Part D: Bit error rate for BPSK in AWGN: 0.5 * erfc(sqrt(Eb/N0_lin))."""
    ebn0_lin = 10.0 ** (ebn0_db / 10.0)
    return 0.5 * math.erfc(math.sqrt(ebn0_lin))
```

### 7.2 Generated Plots & Visualizations
The script generates four analytical plots saved in the workspace:
1. `partA.png`: Capacity vs. SNR ($0\text{ to }40\text{ dB}$) for Cat5e, Cat6, and Cat6a with marked $25\text{ dB}$ operating point.
2. `partB.png`: Power attenuation vs. distance for copper ($8\text{ dB/km}$) and optical fibre ($0.3\text{ dB/km}$) with the $-40\text{ dBm}$ receiver sensitivity line.
3. `partC.png`: Received wireless power vs. distance ($0\text{ to }20\text{ km}$) for $900\text{ MHz}$, $2.4\text{ GHz}$, and $5\text{ GHz}$.
4. `partD.png`: Semilogarithmic plot of BER vs. $E_b/N_0$ ($0\text{ to }12\text{ dB}$) with horizontal threshold at $10^{-3}$.

---

## 8. Comprehensive Viva & Exam Preparation Guide

### Q1: What is the fundamental difference between Nyquist's theorem and Shannon's theorem?
**Answer:** Nyquist's theorem establishes the maximum data rate for an idealized, noiseless channel based purely on bandwidth and discrete signal levels ($C = 2B\log_2 M$). Shannon's theorem establishes the absolute, unbreakable theoretical limit for an actual physical channel corrupted by thermal noise ($C = B\log_2(1 + S/N)$), independent of the number of signal levels.

### Q2: Why can't we increase channel capacity indefinitely by simply adding more signal levels?
**Answer:** Adding more signal levels decreases the distance between adjacent voltage thresholds. In the presence of noise, random thermal voltage fluctuations will exceed this reduced margin, causing the receiver to misinterpret one level for another, creating severe bit errors.

### Q3: Why does optical fibre have such low attenuation compared to copper?
**Answer:** Copper loses energy through electrical resistance ($I^2 R$) and electromagnetic radiation. Optical fibre uses Total Internal Reflection (TIR) inside ultra-pure silica glass core. At the $1550\text{ nm}$ infrared window, Rayleigh scattering and absorption are minimized, resulting in attenuation as low as $0.2–0.3\text{ dB/km}$.

### Q4: Explain the physical origin of the 100 m limit on standard Ethernet cables.
**Answer:** At $100\text{ MHz}$ signal frequencies, the skin effect and dielectric losses increase Cat5e copper cable attenuation to $220\text{ dB/km}$. Given the standard Ethernet transceiver link budget of $22\text{ dB}$, the signal degrades below the detection threshold at exactly $22 / 220 = 0.1\text{ km} = 100\text{ m}$.

### Q5: In the Friis equation, why does path loss increase with frequency?
**Answer:** Radio waves do not lose energy through friction in a vacuum. However, higher frequencies have shorter wavelengths ($\lambda = c/f$). Because an isotropic receiving antenna's effective capture area is proportional to $\lambda^2 = (c/f)^2$, a higher-frequency antenna physically intercepts a smaller portion of the spherical expanding wavefront.

### Q6: What is the difference between SNR and $E_b/N_0$?
**Answer:** SNR measures the ratio of total signal power to noise power across the entire channel bandwidth (a transmission capacity metric). $E_b/N_0$ is the normalized signal-to-noise ratio per bit of information, measuring energy per bit divided by noise spectral density (a bit-level reliability and error-rate metric).

---
*End of Lab 2 Report · Prepared for CS353 Computer Networks*

