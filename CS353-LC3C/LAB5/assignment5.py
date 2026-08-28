def run_gbn(payloads, W, drops, verbose=False):
    N = len(payloads)
    base = 0
    expected = 0
    transmissions = 0
    rounds = 0
    delivery_order = []
    
    # Tracks the round a frame was last sent to handle 1-round timeouts
    sent_in_round = {i: None for i in range(N)}
    
    while base < N:
        rounds += 1
        current_sends = []
        
        # 1. Send Phase
        for seq in range(base, min(base + W, N)):
            if sent_in_round[seq] is None or sent_in_round[seq] < rounds:
                sent_in_round[seq] = rounds
                current_sends.append(seq)
                transmissions += 1
                
        # 2. Data Channel & 3. Receiver
        arrived_frames = [seq for seq in current_sends if (rounds, "data", seq) not in drops]
        ack_to_send = None
        
        if arrived_frames:
            # Must process in ascending sequence order
            for seq in sorted(arrived_frames):
                if seq == expected:
                    delivery_order.append(payloads[seq])
                    expected += 1
            # Send one cumulative ACK if at least one frame arrived
            ack_to_send = expected - 1
            
        old_base = base
        # 4. Acknowledgement Channel & 5. Sender processes ACKs
        ack_received = False
        if ack_to_send is not None and ack_to_send >= 0:
            if (rounds, "ack", ack_to_send) not in drops:
                ack_received = True
                if ack_to_send >= base:
                    base = ack_to_send + 1
                    
        if verbose and current_sends:
            if len(current_sends) == 1:
                send_str = f"send {current_sends[0]}"
            elif current_sends == list(range(current_sends[0], current_sends[-1]+1)):
                send_str = f"send {current_sends[0]} to {current_sends[-1]}"
                if rounds > 1 and current_sends[0] == old_base:
                    send_str += " again"
            else:
                send_str = f"send {current_sends}"
                
            lost = [s for s in current_sends if s not in arrived_frames]
            if not lost:
                arrive_str = "all arrive"
            else:
                arr = arrived_frames
                if len(arr) == 1:
                    arrive_str = f"frame {arr[0]} arrive ({lost[0]} lost)"
                elif arr and arr == list(range(arr[0], arr[-1]+1)):
                    arrive_str = f"frames {arr[0]} to {arr[-1]} arrive ({lost[0]} lost)"
                else:
                    arrive_str = f"frames {arr} arrive ({len(lost)} lost)"
            
            if ack_received:
                ack_str = f"cumulative ACK {ack_to_send}"
            else:
                ack_str = "no acknowledgement"
                
            base_str = f"base becomes {base}" if base != old_base else f"base stays {old_base}"
            print(f"Go-Back-N. Round {rounds}: {send_str}, {arrive_str}, {ack_str}, {base_str}.")
            
        # 6. Timeout carry-over is inherently handled; frames unacknowledged 
        # by the end of this round will trigger `sent_in_round[seq] < rounds` next loop.

    return transmissions, rounds, delivery_order


def run_sr(payloads, W, drops, verbose=False):
    N = len(payloads)
    base = 0
    recv_base = 0
    transmissions = 0
    rounds = 0
    delivery_order = []
    
    sent_in_round = {i: None for i in range(N)}
    acked = {i: False for i in range(N)}
    recv_buffer = {}
    
    while base < N:
        rounds += 1
        current_sends = []
        
        # 1. Send Phase
        for seq in range(base, min(base + W, N)):
            if not acked[seq]:
                if sent_in_round[seq] is None or sent_in_round[seq] < rounds:
                    sent_in_round[seq] = rounds
                    current_sends.append(seq)
                    transmissions += 1
                    
        # 2. Data Channel & 3. Receiver
        arrived_frames = [seq for seq in current_sends if (rounds, "data", seq) not in drops]
        acks_to_send = []
        
        for seq in sorted(arrived_frames):
            if recv_base <= seq < recv_base + W:
                recv_buffer[seq] = payloads[seq]
                acks_to_send.append(seq)
            elif seq < recv_base:
                # Re-acknowledge a frame whose number is below the window base
                acks_to_send.append(seq)
                
        # Deliver the contiguous run starting at the receive base
        while recv_base in recv_buffer:
            delivery_order.append(recv_buffer.pop(recv_base))
            recv_base += 1
            
        old_base = base
        # 4. Acknowledgement Channel & 5. Sender processes ACKs
        acks_sent = []
        for ack in acks_to_send:
            if (rounds, "ack", ack) not in drops:
                acks_sent.append(ack)
                if not acked[ack]:
                    acked[ack] = True
                    
        # Advance sender base over contiguous run of acknowledged numbers
        while base < N and acked[base]:
            base += 1
            
        if verbose and current_sends:
            if len(current_sends) == 1:
                send_str = f"send only {current_sends[0]}" if rounds > 1 else f"send {current_sends[0]}"
            elif current_sends == list(range(current_sends[0], current_sends[-1]+1)):
                send_str = f"send {current_sends[0]} to {current_sends[-1]}"
            else:
                send_str = f"send {current_sends}"

            lost = [s for s in current_sends if s not in arrived_frames]
            if not lost:
                arrive_str = "it arrives" if len(current_sends) == 1 else "all arrive"
            else:
                arr = arrived_frames
                if len(arr) == 1:
                    arrive_str = f"frame {arr[0]} arrive and are buffered"
                elif arr and arr == list(range(arr[0], arr[-1]+1)):
                    arrive_str = f"frames {arr[0]} to {arr[-1]} arrive and are buffered"
                else:
                    arrive_str = f"frames {arr} arrive and are buffered"

            if acks_sent:
                if len(acks_sent) == 1:
                    ack_str = f"ACK {acks_sent[0]}"
                elif acks_sent == list(range(acks_sent[0], acks_sent[-1]+1)):
                    ack_str = f"individual ACKs {acks_sent[0]} to {acks_sent[-1]}"
                else:
                    ack_str = f"individual ACKs {acks_sent}"
            else:
                ack_str = "no acknowledgement"
            
            base_str = f"base becomes {base}" if base != old_base else f"base stays {old_base}"
            print(f"Selective Repeat. Round {rounds}: {send_str}, {arrive_str}, {ack_str}, {base_str}.")
            
    return transmissions, rounds, delivery_order


# --- Test Vectors Harness ---
if __name__ == "__main__":
    scenarios = [
        {"name": "S0", "N": 6, "W": 4, "drops": set()},
        {"name": "S1", "N": 6, "W": 4, "drops": {(1, "data", 2)}},
        {"name": "S2", "N": 8, "W": 8, "drops": {(1, "data", 0)}},
        {"name": "S3", "N": 4, "W": 4, "drops": {(1, "ack", 3)}}
    ]

    for s in scenarios:
        print(f"--- Scenario {s['name']} ---")
        payloads = list(range(s["N"]))
        
        verbose = (s["name"] == "S2")
        gbn_tx, gbn_rds, gbn_del = run_gbn(payloads, s["W"], s["drops"], verbose=verbose)
        print(f"Go-Back-N: {gbn_tx} transmissions, {gbn_rds} rounds")
        
        sr_tx, sr_rds, sr_del = run_sr(payloads, s["W"], s["drops"], verbose=verbose)
        print(f"Selective Repeat: {sr_tx} transmissions, {sr_rds} rounds\n")