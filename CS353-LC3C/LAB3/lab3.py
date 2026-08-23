
import os

def transmit(frame_bytes, corruptions):
    res = bytearray(frame_bytes)
    for index, value in corruptions:
        if index < len(res):
            res[index] = value
    return bytes(res)

# Part A: Byte-count framing
def frame_byte_count(payload):
    if len(payload) > 255:
        raise ValueError("Payload too long for byte count")
    return bytes([len(payload)]) + bytes(payload)

def parse_byte_count(stream):
    payloads = []
    i = 0
    while i < len(stream):
        count = stream[i]
        i += 1
        if i + count <= len(stream):
            payloads.append(bytes(stream[i:i+count]))
            i += count
        else:
            # Framing error or incomplete stream, we just collect what we can
            payloads.append(bytes(stream[i:]))
            break
    return payloads

# Part B: Byte stuffing
FLAG = 0x7E
ESC = 0x7D

def frame_byte_stuff(payload):
    res = bytearray([FLAG])
    for b in payload:
        if b == FLAG or b == ESC:
            res.append(ESC)
            res.append(b)
        else:
            res.append(b)
    res.append(FLAG)
    return bytes(res)

def deframe_byte_stuff(frame):
    if not frame or frame[0] != FLAG or frame[-1] != FLAG:
        return b"" # invalid frame
    
    inner = frame[1:-1]
    res = bytearray()
    i = 0
    while i < len(inner):
        b = inner[i]
        if b == ESC:
            i += 1
            if i < len(inner):
                res.append(inner[i])
        else:
            res.append(b)
        i += 1
    return bytes(res)

# Part C: Bit stuffing
def bit_stuff(payload):
    stuffed_bits = []
    consecutive_ones = 0
    for b in payload:
        for i in range(7, -1, -1):
            bit = (b >> i) & 1
            stuffed_bits.append(bit)
            if bit == 1:
                consecutive_ones += 1
                if consecutive_ones == 5:
                    stuffed_bits.append(0)
                    consecutive_ones = 0
            else:
                consecutive_ones = 0
    
    bit_length = len(stuffed_bits)
    res = bytearray()
    for i in range(0, bit_length, 8):
        byte_val = 0
        chunk = stuffed_bits[i:i+8]
        for j, bit in enumerate(chunk):
            byte_val |= (bit << (7 - j))
        res.append(byte_val)
    return bytes(res), bit_length

def bit_unstuff(stuffed_bytes, bit_length):
    extracted_bits = []
    total_bits_read = 0
    for b in stuffed_bytes:
        for i in range(7, -1, -1):
            if total_bits_read >= bit_length:
                break
            extracted_bits.append((b >> i) & 1)
            total_bits_read += 1
    
    unstuffed_bits = []
    consecutive_ones = 0
    i = 0
    while i < len(extracted_bits):
        bit = extracted_bits[i]
        unstuffed_bits.append(bit)
        if bit == 1:
            consecutive_ones += 1
            if consecutive_ones == 5:
                i += 1
                consecutive_ones = 0
        else:
            consecutive_ones = 0
        i += 1
        
    res = bytearray()
    for i in range(0, len(unstuffed_bits), 8):
        byte_val = 0
        chunk = unstuffed_bits[i:i+8]
        for j, bit in enumerate(chunk):
            byte_val |= (bit << (7 - j))
        res.append(byte_val)
    return bytes(res)

def format_hex(b):
    if type(b) == int:
        return f"{b:02X}"
    return " ".join(f"{x:02X}" for x in b)

def run_tests():
    print("========================================")
    print("Part A: Byte-count framing")
    print("========================================")
    
    payloads = [bytes([0x11, 0x22, 0x33]), bytes([0xAA])]
    stream = frame_byte_count(payloads[0]) + frame_byte_count(payloads[1])
    
    # Clean delivery
    delivered = transmit(stream, [])
    recovered = parse_byte_count(delivered)
    print(f"Method 2 (Clean): Expected [11 22 33] and [AA]")
    print(f"                 Got {[format_hex(p) for p in recovered]}")
    
    # Corrupted delivery
    corrupted = transmit(stream, [(0, 0x05)])
    print(f"\nMethod 3 (Corrupted in transit): Delivered {format_hex(corrupted)}")
    recovered_corrupted = parse_byte_count(corrupted)
    print(f"         Recovered payloads: {[format_hex(p) for p in recovered_corrupted]}")
    print("\nExplanation:")
    print("The corruption changes the first frame's count byte from 03 to 05.")
    print("The receiver now reads 5 bytes as the first payload: 11 22 33 01 AA.")
    print("After reading these 5 bytes, the receiver looks for the next frame count byte,")
    print("but there is no data left. Because of the framing error, it loses synchronization,")
    print("and cannot find the boundary of any following frame. Number of correct original frames recovered: 0.")

    print("\n========================================")
    print("Part B: Byte stuffing")
    print("========================================")
    
    tests_b = [
        ("Method 4", bytes([0x11, 0x22]), "7E 11 22 7E"),
        ("Method 5", bytes([0x7E]), "7E 7D 7E 7E"),
        ("Method 6", bytes([0x7D]), "7E 7D 7D 7E"),
        ("Method 7", bytes([0x7D, 0x7E]), "7E 7D 7D 7D 7E 7E"),
    ]
    for name, payload, expected in tests_b:
        framed = frame_byte_stuff(payload)
        delivered = transmit(framed, [])
        recovered = deframe_byte_stuff(delivered)
        print(f"{name}: Input {format_hex(payload)}")
        print(f"  Expected: {expected}")
        print(f"  Output:   {format_hex(delivered)}")
        if recovered != payload:
            print(f"  FAILED round trip! Got {format_hex(recovered)}")
            
    print("\n========================================")
    print("Part C: Bit stuffing")
    print("========================================")
    tests_c = [
        ("Method 8", bytes([0xFF]), "FB 80", 9),
        ("Method 9", bytes([0x7E]), "7D 00", 9),
        ("Method 10", bytes([0xFF, 0xFF]), "FB EF A0", 19),
    ]
    for name, payload, exp_hex, exp_len in tests_c:
        stuffed, bit_len = bit_stuff(payload)
        delivered = transmit(stuffed, [])
        recovered = bit_unstuff(delivered, bit_len)
        print(f"{name}: Input {format_hex(payload)}")
        print(f"  Expected: {exp_hex}, length {exp_len}")
        print(f"  Output:   {format_hex(delivered)}, length {bit_len}")
        if recovered != payload:
            print(f"  FAILED round trip! Got {format_hex(recovered)}")

def overhead_analysis():
    print("\n========================================")
    print("Part D: Overhead Analysis")
    print("========================================")
    
    random_payload = os.urandom(100)
    
    # Byte stuffing overhead
    byte_stuffed = frame_byte_stuff(random_payload)
    overhead_byte_random = (len(byte_stuffed) - len(random_payload)) / len(random_payload) * 100
    
    worst_payload_byte = bytes([FLAG] * 100)
    byte_stuffed_worst = frame_byte_stuff(worst_payload_byte)
    # The framed size is payload size + 100 escapes + 2 flags
    overhead_byte_worst = (len(byte_stuffed_worst) - len(worst_payload_byte)) / len(worst_payload_byte) * 100
    
    print(f"Byte stuffing overhead (100 byte random): {overhead_byte_random:.2f}%")
    print(f"Byte stuffing overhead (100 byte worst): {overhead_byte_worst:.2f}%")
    print("Worst-case byte stuffing input: Payload consisting entirely of FLAG (0x7E) or ESC (0x7D) bytes.")
    print("Justification: This forces the maximum number of ESC bytes to be inserted (one for every payload byte).")
    
    # Bit stuffing overhead
    stuffed_bits_random, bit_len_random = bit_stuff(random_payload)
    overhead_bit_random = (bit_len_random - (len(random_payload) * 8)) / (len(random_payload) * 8) * 100
    
    worst_payload_bit = bytes([0xFF] * 100) # all 1s
    stuffed_bits_worst, bit_len_worst = bit_stuff(worst_payload_bit)
    overhead_bit_worst = (bit_len_worst - (len(worst_payload_bit) * 8)) / (len(worst_payload_bit) * 8) * 100
    
    print(f"\nBit stuffing overhead (100 byte random): {overhead_bit_random:.2f}%")
    print(f"Bit stuffing overhead (100 byte worst): {overhead_bit_worst:.2f}%")
    print("Worst-case bit stuffing input: Payload consisting entirely of 0xFF (11111111) bytes.")
    print("Justification: This produces maximum sequences of continuous 1s, forcing the maximum number of 0 bits to be stuffed (1 bit every 5 consecutive 1s).")

    print(f"\nComparing the two methods' worst-case overhead:")
    if overhead_byte_worst > overhead_bit_worst:
        print(f"Byte stuffing has the larger worst-case overhead ({overhead_byte_worst:.2f}% vs {overhead_bit_worst:.2f}%).")
    else:
        print(f"Bit stuffing has the larger worst-case overhead ({overhead_bit_worst:.2f}% vs {overhead_byte_worst:.2f}%).")

if __name__ == '__main__':
    run_tests()
    overhead_analysis()
