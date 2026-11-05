#!/usr/bin/env python3
"""
CS353 - Computer Networks Lab 11 / Lab 12: Quality of Service at a Router
Author: Implementation for QoS Mechanisms

Four QoS mechanisms implemented:
1. Admission Control (Parekh-Gallagher Test)
2. Traffic Policing (Token Bucket - Drop non-conforming)
3. Traffic Shaping (Token Bucket - Buffer and smooth excess)
4. Packet Scheduling (Weighted Fair Queuing vs. FIFO)
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple, Any, Optional


# =====================================================================
# Required Appendix Interfaces
# =====================================================================

def admit(requests: List[Dict[str, Any]], C: float) -> List[Dict[str, Any]]:
    """
    Part A: Admission Control using the Parekh-Gallagher Test.
    
    A flow i is admissible iff:
        (W_i / ΣW) * C >= R_i
    holds for EVERY admitted flow after flow i is added, where ΣW is the 
    total weight of all admitted flows including flow i.
    
    Parameters:
        requests: List of dicts, each with keys 'flow' (or 'name'), 'weight', 'rate'
        C: Total link capacity (e.g. 10.0 Mbps)
        
    Returns:
        List of decision records for each request in order.
    """
    admitted_flows: List[Dict[str, Any]] = []
    decisions: List[Dict[str, Any]] = []

    for req in requests:
        flow_id = req.get('flow', req.get('name', 'unknown'))
        weight = float(req['weight'])
        rate = float(req['rate'])

        # Candidate set if we add this flow
        candidate_flows = admitted_flows + [{'flow': flow_id, 'weight': weight, 'rate': rate}]
        total_weight = sum(f['weight'] for f in candidate_flows)

        # Parekh-Gallagher test: Check if EVERY flow in candidate_flows gets >= its requested rate
        all_satisfied = True
        guaranteed_rates = {}
        for f in candidate_flows:
            guaranteed = (f['weight'] / total_weight) * C
            guaranteed_rates[f['flow']] = guaranteed
            if guaranteed < f['rate'] - 1e-9:  # floating point tolerance
                all_satisfied = False

        if all_satisfied:
            admitted_flows = candidate_flows
            decision = {
                'flow': flow_id,
                'weight': weight,
                'rate': rate,
                'admitted': True,
                'status': 'ADMITTED',
                'total_weight': total_weight,
                'guaranteed_rate': guaranteed_rates[flow_id],
                'all_guaranteed_rates': guaranteed_rates,
                'reason': f"Guaranteed rate {guaranteed_rates[flow_id]:.2f} Mbps >= requested {rate:.2f} Mbps; all previous guarantees intact."
            }
        else:
            decision = {
                'flow': flow_id,
                'weight': weight,
                'rate': rate,
                'admitted': False,
                'status': 'REJECTED',
                'total_weight': total_weight,
                'guaranteed_rate': guaranteed_rates[flow_id],
                'all_guaranteed_rates': guaranteed_rates,
                'reason': f"Guaranteed rate {guaranteed_rates[flow_id]:.2f} Mbps < requested {rate:.2f} Mbps (or breaks existing flow guarantee)."
            }

        decisions.append(decision)

    return decisions


def police(trace: List[float], r: float, b: float, packet_size: float = 1.0) -> List[Dict[str, Any]]:
    """
    Part B: Traffic Policing using a Token Bucket.
    
    Tokens accrue at rate r up to capacity b. The bucket starts full.
    A packet of size packet_size is conforming if at least packet_size tokens
    are present. Non-conforming packets are DROPPED immediately (no buffering).
    
    Parameters:
        trace: List of arrival times for each packet.
        r: Token fill rate (tokens per time unit).
        b: Token bucket capacity (maximum tokens).
        packet_size: Size in tokens consumed per packet (default 1.0).
        
    Returns:
        List of dicts per packet with arrival time, tokens before, action ('PASS'/'DROP'), tokens after.
    """
    tokens = float(b)  # bucket starts full
    last_time = trace[0] if trace else 0.0
    results: List[Dict[str, Any]] = []

    for i, t in enumerate(trace):
        # Accumulate tokens accrued over time elapsed
        dt = max(0.0, t - last_time)
        tokens = min(b, tokens + dt * r)
        last_time = t

        tokens_before = tokens
        if tokens >= packet_size:
            tokens -= packet_size
            action = 'PASS'
            conforming = True
        else:
            action = 'DROP'
            conforming = False

        results.append({
            'packet_index': i + 1,
            'arrival_time': t,
            'tokens_before': tokens_before,
            'action': action,
            'conforming': conforming,
            'tokens_after': tokens
        })

    return results


def shape(trace: List[float], r: float, b: float, packet_size: float = 1.0) -> List[Dict[str, Any]]:
    """
    Part C: Traffic Shaping using a Token Bucket with a FIFO buffer.
    
    Non-conforming packets are held in a buffer and released once enough
    tokens have accrued. Output is smoothed to token rate r; no packet is dropped.
    
    Parameters:
        trace: List of arrival times for each packet.
        r: Token fill rate (tokens per time unit).
        b: Token bucket capacity (maximum tokens).
        packet_size: Size in tokens consumed per packet (default 1.0).
        
    Returns:
        List of dicts per packet with arrival time, release time, and delay.
    """
    tokens = float(b)  # bucket starts full
    current_time = trace[0] if trace else 0.0
    results: List[Dict[str, Any]] = []

    for i, t in enumerate(trace):
        # If time has advanced past current_time, tokens have accrued
        if t > current_time:
            dt = t - current_time
            tokens = min(b, tokens + dt * r)
            current_time = t

        # If we have enough tokens, release immediately at current_time
        if tokens >= packet_size:
            tokens -= packet_size
            release_time = current_time
        else:
            # Not enough tokens: wait until (packet_size - tokens) accrue
            needed = packet_size - tokens
            wait_time = needed / r
            current_time += wait_time
            tokens = 0.0
            release_time = current_time

        delay = release_time - t
        results.append({
            'packet_index': i + 1,
            'arrival_time': t,
            'release_time': release_time,
            'delay': delay
        })

    return results


def wfq(flows: Dict[str, Dict[str, Any]]) -> Tuple[Dict[str, float], List[str]]:
    """
    Part D: Weighted Fair Queuing (WFQ) Packet Scheduler.
    
    For each packet k of flow i:
        Finish Number F_k = max(arrival_k, prev_finish_in_flow) + length_k / weight_i
    Packets are sent in increasing order of finish number.
    
    Parameters:
        flows: Dict mapping flow_name -> {
            'weight': float,
            'packets': List of tuples (packet_name, arrival_time, length)
        }
        
    Returns:
        Tuple of:
          - Dict mapping packet_name -> finish_number
          - List of packet_names in transmission order (sorted by finish number)
    """
    packet_finish_numbers: Dict[str, float] = {}
    packet_details: List[Dict[str, Any]] = []

    for flow_id, flow_info in flows.items():
        weight = float(flow_info['weight'])
        packets = flow_info['packets']
        prev_finish = 0.0

        for pkt in packets:
            name, arrival, length = pkt
            arrival = float(arrival)
            length = float(length)

            start_time = max(arrival, prev_finish)
            finish_time = start_time + (length / weight)
            prev_finish = finish_time

            packet_finish_numbers[name] = finish_time
            packet_details.append({
                'name': name,
                'flow': flow_id,
                'weight': weight,
                'arrival': arrival,
                'length': length,
                'start_virtual': start_time,
                'finish_number': finish_time
            })

    # Sort packets by finish number. Tie breaker: arrival time, then name.
    sorted_packets = sorted(packet_details, key=lambda p: (p['finish_number'], p['arrival'], p['name']))
    output_order = [p['name'] for p in sorted_packets]

    return packet_finish_numbers, output_order


def fifo(flows: Dict[str, Dict[str, Any]]) -> List[str]:
    """
    Part D: First-In First-Out (FIFO) Packet Scheduler.
    
    Packets are sent strictly in arrival order.
    Tie-breaking: flow order, then packet sequence in flow.
    
    Parameters:
        flows: Dict mapping flow_name -> {
            'weight': float,
            'packets': List of tuples (packet_name, arrival_time, length)
        }
        
    Returns:
        List of packet_names in arrival order.
    """
    all_packets: List[Dict[str, Any]] = []
    
    for flow_id, flow_info in flows.items():
        for pkt in flow_info['packets']:
            name, arrival, length = pkt
            all_packets.append({
                'name': name,
                'flow': flow_id,
                'arrival': float(arrival),
                'length': float(length)
            })

    # Sort strictly by arrival time. Stable order preserves input sequence.
    sorted_by_arrival = sorted(all_packets, key=lambda p: p['arrival'])
    return [p['name'] for p in sorted_by_arrival]


# =====================================================================
# Main Simulation & Demonstration Runner
# =====================================================================

def run_all_lab_experiments() -> None:
    print("=" * 78)
    print("CS353 NETWORK QoS LAB: COMPLETE SIMULATION & VERIFICATION")
    print("=" * 78)

    # -----------------------------------------------------------------
    # Part A: Admission Control
    # -----------------------------------------------------------------
    print("\n" + "#" * 78)
    print("PART A: ADMISSION CONTROL (Parekh-Gallagher Model)")
    print("#" * 78)
    C = 10.0  # Mbps
    requests = [
        {'flow': 'f1', 'weight': 1.0, 'rate': 2.0},
        {'flow': 'f2', 'weight': 1.0, 'rate': 2.0},
        {'flow': 'f3', 'weight': 2.0, 'rate': 4.0},
        {'flow': 'f4', 'weight': 1.0, 'rate': 3.0},
    ]

    print(f"Link Capacity C = {C} Mbps")
    print("Incoming Setup Requests:")
    print(f"  {'Flow':<6} | {'Weight':<8} | {'Requested Rate (Mbps)':<22}")
    print("  " + "-" * 42)
    for r in requests:
        print(f"  {r['flow']:<6} | {r['weight']:<8} | {r['rate']:<22.2f}")

    decisions = admit(requests, C)

    print("\nSequential Admission Decisions:")
    print(f"  {'Flow':<6} | {'Req Rate':<10} | {'Total W':<8} | {'Guaranteed':<12} | {'Decision':<10} | {'Reason'}")
    print("  " + "-" * 74)
    for d in decisions:
        print(f"  {d['flow']:<6} | {d['rate']:<10.1f} | {d['total_weight']:<8.1f} | {d['guaranteed_rate']:<12.2f} | {d['status']:<10} | {d['reason']}")

    # Confirm expected results
    assert decisions[0]['admitted'] is True, "f1 should be admitted"
    assert decisions[1]['admitted'] is True, "f2 should be admitted"
    assert decisions[2]['admitted'] is True, "f3 should be admitted"
    assert decisions[3]['admitted'] is False, "f4 should be rejected"
    assert abs(decisions[3]['guaranteed_rate'] - 2.0) < 1e-6, "f4 guaranteed rate should be 2.0 Mbps"
    print("\n[CONFIRMED] f1, f2, and f3 are ADMITTED; f4 is REJECTED (guaranteed only 2.0 Mbps against 3.0 Mbps requested).")

    # Written Questions Part A
    print("\n--- Part A Written Answers ---")
    print("Question 4a: Which flow's guarantee does the rejection protect?")
    print("Answer:")
    print("  1. Primary: Rejection directly protects f4's OWN contract guarantee, because the network")
    print("     cannot fulfill f4's requested service level (3 Mbps) under the committed fair-share rate (2 Mbps).")
    print("  2. Existing flows: If f4 were forcefully granted 3 Mbps (requiring weight W >= 12/7 ≈ 1.714),")
    print("     the total requested bandwidth (2 + 2 + 4 + 3 = 11 Mbps) would exceed the physical link capacity")
    print("     (10 Mbps). This would degrade the guaranteed rates of previously admitted flows f1, f2, and f3")
    print("     below their contractual commitments (e.g., at W_4 = 2, f1 and f2 get only 1.67 Mbps < 2 Mbps,")
    print("     and f3 gets only 3.33 Mbps < 4 Mbps). Hence, rejection protects flows f1, f2, and f3.")
    print("Question 4b: What weight or rate would f4 need to be admitted?")
    print("Answer:")
    print("  - Rate requirement: With its given weight W_4 = 1, total weight is ΣW = 4 + 1 = 5.")
    print("    f4 is guaranteed (1/5) * 10 = 2.0 Mbps. Therefore, f4 would be admitted if its requested rate")
    print("    is reduced to R_4 <= 2.0 Mbps.")
    print("  - Weight note: No weight alone can admit f4 at R_4 = 3.0 Mbps because the sum of requested rates")
    print("    (2 + 2 + 4 + 3 = 11 Mbps) strictly exceeds link capacity C = 10 Mbps. The link has only")
    print("    10 - (2 + 2 + 4) = 2.0 Mbps of unallocated capacity.")

    # -----------------------------------------------------------------
    # Part B: Traffic Policing
    # -----------------------------------------------------------------
    print("\n" + "#" * 78)
    print("PART B: TRAFFIC POLICING (Token Bucket - Drop Excess)")
    print("#" * 78)
    r = 1.0  # token / time unit
    b = 4.0  # tokens capacity
    # Trace: burst of 6 packets at t=0, then single packets at t=5 and t=6
    trace = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 5.0, 6.0]

    print(f"Token Bucket Parameters: fill rate r = {r} token/unit, capacity b = {b} tokens (starts full).")
    print(f"Packet Size L = 1 token. Packet Arrival Trace: {trace}")

    police_results = police(trace, r, b)

    print("\nPolicing Execution Trace:")
    print(f"  {'Pkt #':<6} | {'Arrival':<8} | {'Tokens Before':<15} | {'Action':<8} | {'Tokens After':<15}")
    print("  " + "-" * 60)
    for res in police_results:
        print(f"  {res['packet_index']:<6} | {res['arrival_time']:<8.1f} | {res['tokens_before']:<15.2f} | {res['action']:<8} | {res['tokens_after']:<15.2f}")

    passed_count = sum(1 for res in police_results if res['action'] == 'PASS')
    dropped_count = sum(1 for res in police_results if res['action'] == 'DROP')

    # Confirm expected results
    assert [res['action'] for res in police_results] == ['PASS', 'PASS', 'PASS', 'PASS', 'DROP', 'DROP', 'PASS', 'PASS']
    assert passed_count == 6 and dropped_count == 2
    print(f"\n[CONFIRMED] {passed_count} packets passed, {dropped_count} packets dropped.")
    print("Packets 1-4 pass, Packets 5-6 drop, Packets 7-8 (at times 5 and 6) pass.")

    # Written Question Part B
    print("\n--- Part B Written Answer ---")
    print("Question 3: Explain why exactly two packets are dropped, in terms of bucket capacity.")
    print("Answer:")
    print("  The bucket capacity is b = 4 tokens, and it starts full. At time t = 0, a burst of 6 packets")
    print("  arrives simultaneously (Δt = 0), meaning zero new tokens accrue during the burst.")
    print("  Each packet consumes L = 1 token. The first 4 packets consume all 4 tokens in the bucket,")
    print("  leaving 0 tokens. When packets 5 and 6 arrive at t = 0, there are 0 tokens available (< 1 token needed).")
    print("  Because policing does not store or buffer non-conforming packets, the router immediately drops")
    print("  the remaining 6 - 4 = 2 packets.")

    # -----------------------------------------------------------------
    # Part C: Traffic Shaping
    # -----------------------------------------------------------------
    print("\n" + "#" * 78)
    print("PART C: TRAFFIC SHAPING (Token Bucket - Buffer Excess)")
    print("#" * 78)

    shape_results = shape(trace, r, b)

    print("\nShaping Execution Trace:")
    print(f"  {'Pkt #':<6} | {'Arrival':<8} | {'Release Time':<14} | {'Delay':<8} | {'Status'}")
    print("  " + "-" * 52)
    for s in shape_results:
        print(f"  {s['packet_index']:<6} | {s['arrival_time']:<8.1f} | {s['release_time']:<14.1f} | {s['delay']:<8.1f} | DELIVERED (Buffered)")

    expected_releases = [0.0, 0.0, 0.0, 0.0, 1.0, 2.0, 5.0, 6.0]
    actual_releases = [s['release_time'] for s in shape_results]
    assert actual_releases == expected_releases, f"Expected {expected_releases}, got {actual_releases}"
    print("\n[CONFIRMED] Packets 1-4 leave at t = 0, packet 5 leaves at t = 1, packet 6 leaves at t = 2;")
    print("packets 7 and 8 leave immediately at t = 5 and t = 6. Zero packets dropped.")

    # Written Questions Part C
    print("\n--- Part C Written Answer ---")
    print("Question 3a: Report the delay each packet experienced, and compare with Part B.")
    print("Delays experienced in Shaping:")
    for s in shape_results:
        print(f"  Packet {s['packet_index']} (arr={s['arrival_time']:.0f}): Delay = {s['delay']:.1f} time units (released at t={s['release_time']:.1f})")
    print("Comparison with Part B:")
    print("  In Part B (Policing), packets 5 and 6 were DROPPED (100% loss, infinite delay / never delivered).")
    print("  In Part C (Shaping), NO packets were dropped (0% loss); instead, packets 5 and 6 experienced small")
    print("  delays of 1.0 and 2.0 time units respectively to conform to the token arrival rate.")
    print("\nQuestion 3b: State the single difference between shaping and policing that produces drops in one and delays in the other.")
    print("Answer:")
    print("  The single fundamental difference is the presence of a PACKET BUFFER (QUEUE).")
    print("  - A policer has NO buffer: non-conforming packets are immediately dropped (or marked) upon arrival.")
    print("  - A shaper has a BUFFER: non-conforming packets are held in a queue and delayed until sufficient tokens")
    print("    accrue, trading buffer latency for zero packet loss.")

    # -----------------------------------------------------------------
    # Part D: Packet Scheduling (WFQ vs FIFO)
    # -----------------------------------------------------------------
    print("\n" + "#" * 78)
    print("PART D: PACKET SCHEDULING (Weighted Fair Queuing vs. FIFO)")
    print("#" * 78)

    flows = {
        'Flow 1': {
            'weight': 1.0,
            'packets': [('A', 0.0, 8.0), ('F', 10.0, 6.0)]
        },
        'Flow 2': {
            'weight': 1.0,
            'packets': [('B', 5.0, 6.0), ('D', 8.0, 9.0), ('H', 20.0, 8.0)]
        },
        'Flow 3': {
            'weight': 2.0,
            'packets': [('C', 5.0, 10.0), ('E', 8.0, 8.0), ('G', 11.0, 10.0)]
        }
    }

    print("Admitted Flows and Packets (carried over from Part A):")
    for f_name, f_info in flows.items():
        pkts_str = ", ".join([f"{p[0]}(arr={p[1]:.0f}, len={p[2]:.0f})" for p in f_info['packets']])
        print(f"  {f_name} (weight = {f_info['weight']:.0f}): {pkts_str}")

    finish_numbers, wfq_order = wfq(flows)
    fifo_order = fifo(flows)

    print("\nWFQ Finish Number Computations (F = max(arrival, prev_finish) + length / weight):")
    print(f"  {'Pkt':<5} | {'Flow':<8} | {'Weight':<8} | {'Arrival':<8} | {'Length':<8} | {'Finish Number F'}")
    print("  " + "-" * 56)
    # List in sorted order of finish number
    sorted_items = sorted(finish_numbers.items(), key=lambda x: x[1])
    for pkt_name, f_num in sorted_items:
        # find flow
        fl = next(k for k, v in flows.items() if any(p[0] == pkt_name for p in v['packets']))
        pkt_data = next(p for p in flows[fl]['packets'] if p[0] == pkt_name)
        print(f"  {pkt_name:<5} | {fl:<8} | {flows[fl]['weight']:<8.0f} | {pkt_data[1]:<8.0f} | {pkt_data[2]:<8.0f} | {f_num:<10.1f}")

    expected_finish_numbers = {'A': 8.0, 'C': 10.0, 'B': 11.0, 'E': 14.0, 'F': 16.0, 'G': 19.0, 'D': 20.0, 'H': 28.0}
    expected_wfq_order = ['A', 'C', 'B', 'E', 'F', 'G', 'D', 'H']

    for k, v in expected_finish_numbers.items():
        assert abs(finish_numbers[k] - v) < 1e-6, f"Mismatch for {k}: expected {v}, got {finish_numbers[k]}"
    assert wfq_order == expected_wfq_order, f"Expected {expected_wfq_order}, got {wfq_order}"

    print(f"\n[CONFIRMED] Finish numbers: {', '.join([f'{k} {v:.0f}' for k, v in sorted_items])}")
    print(f"[CONFIRMED] WFQ Output Order:  {' -> '.join(wfq_order)}")
    print(f"[CONFIRMED] FIFO Arrival Order: {' -> '.join(fifo_order)}")

    # Written Questions Part D
    print("\n--- Part D Written Answers ---")
    print("Question 4a: Compare the two orders and explain how the weight-2 flow is served.")
    print("Comparison:")
    print(f"  - WFQ Order:  {', '.join(wfq_order)}")
    print(f"  - FIFO Order: {', '.join(fifo_order)}")
    print("Explanation of how Flow 3 (weight = 2) is served:")
    print("  - In WFQ, a flow's finish number increments by length / weight.")
    print("    Because Flow 3 has weight 2 (twice that of Flow 1 and Flow 2), its virtual transmission time")
    print("    per byte is cut in half (10/2 = 5 for C, 8/2 = 4 for E, 10/2 = 5 for G).")
    print("  - Consequently, even though Packet C (length 10) arrives at time 5 alongside Packet B (length 6),")
    print("    Packet C's finish number is 5 + 10/2 = 10, whereas Packet B's finish number is 5 + 6/1 = 11.")
    print("    Therefore, Packet C is scheduled BEFORE Packet B!")
    print("  - Similarly, Packet E (arrival 8, length 8) finishes at 10 + 8/2 = 14, jumping ahead of Flow 1's")
    print("    Packet F (finish 16) and Flow 2's Packet D (arrival 8, length 9, finish 20).")
    print("  - Under FIFO, Flow 3 would be stuck behind earlier arrivals or equal-arrival ties regardless of weight.")
    print("    WFQ ensures Flow 3 receives exactly twice the bandwidth share of the link compared to Flows 1 and 2.")

    print("\nQuestion 4b: How does Weighted Fair Queuing protect a flow from being starved by another?")
    print("Answer:")
    print("  - In FIFO, an aggressive or misbehaving flow that floods packets can monopolize the queue and link,")
    print("    causing severe delay or complete starvation for all other flows.")
    print("  - In WFQ, each flow maintains its own virtual queue state. A packet's finish number depends on the")
    print("    PREVIOUS finish number of that same flow (max(arrival, prev_finish) + length / weight).")
    print("  - If an aggressive flow transmits a massive burst of packets, its finish numbers advance far into")
    print("    the future (e.g., F1, F2 = F1 + L/w, F3 = F2 + L/w, ...).")
    print("  - Meanwhile, an idle or well-behaved flow that suddenly sends a packet will have its finish number")
    print("    computed starting from its current arrival time (max(arrival, 0) + length/weight), resulting in a")
    print("    much smaller finish number. The scheduler immediately serves the conforming flow's packet ahead")
    print("    of the backlog of the aggressive flow.")
    print("  - Thus, WFQ provides strict FLOW ISOLATION: every flow i is mathematically guaranteed a minimum service")
    print("    rate of (W_i / ΣW) * C over any active period, making starvation impossible.")

    print("\n" + "=" * 78)
    print("ALL TESTS PASSED SUCCESSFULLY AND ALL RESULTS VERIFIED AGAINST SPECIFICATION!")
    print("=" * 78)


if __name__ == '__main__':
    run_all_lab_experiments()

