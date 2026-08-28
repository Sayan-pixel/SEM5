# Part C: Comparison

1. **Total transmissions and list of resent sequence numbers for S1 and S2:**
   - **Scenario S1:** 
     - **Go-Back-N:** 8 total transmissions. Resent sequence numbers: `2, 3`.
     - **Selective Repeat:** 7 total transmissions. Resent sequence numbers: `2`.
   - **Scenario S2:** 
     - **Go-Back-N:** 16 total transmissions. Resent sequence numbers: `0, 1, 2, 3, 4, 5, 6, 7`.
     - **Selective Repeat:** 9 total transmissions. Resent sequence numbers: `0`.

2. **Why Go-Back-N resends safely arrived frames and Selective Repeat does not:**
   Go-Back-N utilizes cumulative acknowledgements and strictly discards any out-of-order frames. Thus, if a frame is lost, all subsequent frames in the window are discarded by the receiver, forcing the sender to retransmit the entire outstanding window starting from the lost frame. Selective Repeat uses individual acknowledgements and buffers out-of-order frames, which allows the receiver to retain correctly received frames and the sender to retransmit only the specific frames that were dropped.

3. **Condition for identical behavior:**
   The two protocols behave identically (where Go-Back-N wastes nothing) when operating over a perfectly clean channel with no frame or acknowledgement drops, or alternatively, when the window size (W) is equal to 1.

# Part D: Analysis

1. **Retransmission Overhead:**
   *Overhead is defined as total transmissions divided by the number of payloads.*
   - **Scenario S1 (Window Size 4):**
     - Go-Back-N overhead: 8 / 6 ≈ 1.33
     - Selective Repeat overhead: 7 / 6 ≈ 1.17
   - **Scenario S2 (Window Size 8):**
     - Go-Back-N overhead: 16 / 8 = 2.0
     - Selective Repeat overhead: 9 / 8 = 1.125
   
   **How the gap changes:** The gap in retransmission overhead between the two protocols widens as the window size (W) grows, because Go-Back-N must potentially retransmit up to W frames for a single loss.

2. **Why the difference widens with larger windows and shrinks with near-zero loss rates:**
   With a larger window, a single dropped frame in Go-Back-N causes a larger number of successfully delivered but out-of-order frames to be discarded and subsequently retransmitted. Selective Repeat, however, continues to retransmit only the single dropped frame regardless of the window size, widening the efficiency gap. As the loss rate approaches zero, retransmissions become exceedingly rare, allowing both protocols to transmit exactly N frames with zero overhead, thereby shrinking the efficiency difference between them toward zero.

3. **Sequence-Number-Space Requirement:**
   - **Selective Repeat (>= 2W):** Suppose the window size is W=4 and the sequence number space only has 4 distinct sequence numbers (0, 1, 2, 3). The sender transmits frames 0, 1, 2, 3. The receiver gets them all, buffers/delivers them, sends individual ACKs for 0, 1, 2, 3, and advances its receive window to expect the next sequence of frames, which wrap around to 0, 1, 2, 3. If all the ACKs are dropped in transit, the sender times out and retransmits the *old* frame 0. The receiver, expecting the *new* frame 0, accepts the duplicate as new data, causing data corruption. To avoid this ambiguity between the previous window and the next window, the sequence space must be at least 2W.
   - **Go-Back-N (>= W + 1):** The Go-Back-N receiver only expects exactly one specific sequence number in order (its receive window size is 1). If W=4 and the sequence space is W (0, 1, 2, 3), the sender transmits 0, 1, 2, 3. The receiver gets them all, sends a cumulative ACK for 3, and advances its expected number to 0 (wraparound). If the ACK is lost, the sender times out and retransmits the old frame 0. The receiver, which happens to be expecting 0, accepts it as new data. To disambiguate, we only need a sequence space of W+1. With 5 sequence numbers (0, 1, 2, 3, 4), after receiving 0 to 3, the receiver expects 4. When the sender retransmits old frame 0, the receiver expects 4, recognizes 0 as out-of-order, and safely discards it.
