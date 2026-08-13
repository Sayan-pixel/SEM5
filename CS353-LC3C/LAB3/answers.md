# Lab 2 Answers

## Part A — Bandwidth → bit rate

**1. Nyquist (noiseless) verification**
- Cat5e (100 MHz): M = 2^(1Gbps / (2 * 100MHz)) = 2^5 = 32
- Cat6 (250 MHz): M = 2^(1Gbps / (2 * 250MHz)) = 2^2 = 4
- Cat6a (500 MHz): M = 2^(1Gbps / (2 * 500MHz)) = 2^1 = 2
*Relationship:* The cable with the greatest bandwidth requires the fewest signal levels to achieve the same bit rate.

**4. Three ceilings**
- **Fantasy ceiling:** Nyquist limit. It assumes zero noise in the channel, which is impossible in the real world.
- **Real ceiling:** Shannon limit. It takes into account the noise (SNR), representing a realistic capacity limit.
- **Actual hardware:** Actual hardware will land *below* the Shannon limit, because practical implementations cannot be perfectly efficient at the Shannon boundary.

## Part B — Attenuation → distance

**a. Parameters and Link budget**
- P_tx = 0 dBm
- P_sens = -40 dBm
- Link budget = P_tx - P_sens = 0 - (-40) = 40 dB.

**b. Copper distance**
- d_max = (P_tx - P_sens) / α = 40 dB / 8 dB/km = 5 km.

**c. Fibre distance**
- d_max = 40 dB / 0.3 dB/km = 133.33 km.
- Fibre reaches 133.33 / 5 = 26.67 times further than copper.

**d. Fibre result explanation**
Fibre has significantly lower attenuation than copper (0.3 dB/km vs 8 dB/km). Furthermore, real fibre links can reach even further than this calculation because optical amplifiers can be used along the way to boost the signal, and specific fibre receivers can have even lower sensitivity thresholds than -40 dBm.

**e. Ethernet limit derivation**
- Cat5e at 100 MHz attenuation α = 220 dB/km.
- Link budget = 22 dB.
- d_max = 22 dB / 220 dB/km = 0.1 km = 100 m.
This is the physical origin of the 100 m limit on copper Ethernet.

## Part C: Wireless

**1 & 2. Received power difference at 5 km**
Using FSPL formula:
- Received power decreases as frequency increases.
- Difference between 900 MHz and 5 GHz: 20 * log10(5 GHz / 900 MHz) ≈ 14.89 dB (~15 dB).
- The term in the Friis equation responsible for this gap is `20·log10(f)`. Higher frequencies suffer from greater free-space path loss.

## Part D: Bit error rate

**3. Eb/N0 for BER = 10^-3**
By solving or looking at the graph, the BER reaches 10^-3 at approximately Eb/N0 = 6.8 dB.

**4. Channel one-line summary**
A channel over a span of 5 km, with a capacity bounded by Shannon limit (~832 Mbps for Cat5e at 25 dB SNR), operating at an Eb/N0 of 7 dB achieves a bit error rate (BER) of approximately 8 × 10^-4.
