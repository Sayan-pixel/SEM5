import random

# constants
FLAG = 0x7E
ESC = 0x7D

# helper function for converting byte seq into hexadecimal str
def hex_bytes(data):
    return " ".join(f"{b:02X}" for b in data)

# transmission medium
def transmit(frame_bytes, currpt):
    recv = list(frame_bytes)

    for idx, val in currpt:
        if (0 <= idx < len(recv)):
            recv[idx] = val

    return recv

# -------------------------------------------------
# part a: byte count framing
# -------------------------------------------------

# add one byte that containing the payload length
def byte_count_frame(payload):
    if(len(payload) > 255):
        raise ValueError("Payload can't exceed 255 bytes")

    return [len(payload)] + list(payload)

# a stream that containing multiple byte count frames
def byte_count_stream(payloads):
    stream = []

    for payload in payloads:
        stream.extend(byte_count_frame(payload))

    return stream

# parse a byte count framed stream
def byte_count_parse(stream):
    payloads = []
    i = 0

    while(i < len(stream)):
        count = stream[i]
        i += 1

        # not enough byte for this frame
        if(i + count > len(stream)):
            break

        payload = stream[i:i + count]
        payloads.append(payload)

        i += count

    return payloads

# -------------------------------------------------
# part b: byte stuffing
# -------------------------------------------------

# frame format -> (FLAG + esc payload + FLAG)
# for every FLAG or ESC inside payload is preceded by ESC
def byte_stuff_frame(payload):
    frame = [FLAG]

    for byte in payload:
        if(byte == FLAG or byte == ESC):
            frame.append(ESC)

        frame.append(byte)

    frame.append(FLAG)

    return frame

# recover original payload from a stuffed frame
def byte_stuff_deframe(frame):
    if(len(frame) < 2):
        return []

    # removing beginning and ending FLAG
    data = frame[1:-1]

    payload = []
    i = 0

    while (i < len(data)):

        if(data[i] == ESC):

            # ESC must have a following byte
            if(i + 1 >= len(data)):
                raise ValueError("Invalid ESC sequence")

            payload.append(data[i + 1])
            i += 2

        else:
            payload.append(data[i])
            i += 1

    return payload

# -------------------------------------------------
# part c: bit stuffing
# -------------------------------------------------

# convert bytes into bits : (MSB first) bit 7 -> bit 0
def bytes_to_bits(data):
    bits = []

    for byte in data:

        for bit_pos in range(7, -1, -1):
            bit = (byte >> bit_pos) & 1
            bits.append(bit)

    return bits

# pack bits into bytes : last byte is padded with 0s if less than 8 bits
def pack_bits_into_bytes(bits):
    if(len(bits) == 0):
        return []

    res = []

    for i in range(0, len(bits), 8):
        byte = 0
        chunk = bits[i:i + 8]

        for bit in chunk:
            byte = (byte << 1) | bit

        # padding
        while(len(chunk) < 8):
            byte <<= 1
            chunk.append(0)

        res.append(byte)

    return res

# bit stuffing: insert 0 after every 5 consecutive 1's
def bit_stuff(payload):
    orig_bits = bytes_to_bits(payload)

    stuff_bits = []
    cons_ones = 0

    for bit in orig_bits:

        stuff_bits.append(bit)

        if(bit == 1):
            cons_ones += 1

            if(cons_ones == 5):
                # insert a stuffed 0
                stuff_bits.append(0)
                cons_ones = 0

        else:
            cons_ones = 0

    # convert stuffed bits into actual bytes
    stuff_bytes = pack_bits_into_bytes(stuff_bits)

    return stuff_bytes, len(stuff_bits)

# reverse bit stuffing: only the 1st bit_length bits are considered
def bit_unstuff(stuff_bytes, bit_length):

    bits = bytes_to_bits(stuff_bytes)
    bits = bits[:bit_length]

    unstuff_bit = []
    cons_ones = 0
    i = 0

    while(i < len(bits)):

        bit = bits[i]
        unstuff_bit.append(bit)

        if(bit == 1):
            cons_ones += 1

            if(cons_ones == 5):

                # skip the next 0 (stuffed bit)
                i += 1

                if(i < len(bits) and bits[i] == 0):
                    pass

                cons_ones = 0

        else:
            cons_ones = 0

        i += 1

    # converting bits back to bytes
    result = []

    for i in range(0, len(unstuff_bit), 8):

        chunk = unstuff_bit[i:i + 8]

        if(len(chunk) < 8):
            break

        byte = 0

        for bit in chunk:
            byte = (byte << 1) | bit

        result.append(byte)

    return result

# -------------------------------------------------
# part d: overhead calculation
# -------------------------------------------------

# byte count framing adds exactly one byte
def byte_count_overhead(payload):
    framed = byte_count_frame(payload)

    return ((len(framed) - len(payload)) / len(payload)) * 100


# byte stuffing adds : 2 FLAG bytes + one ESC for every FLAG and ESC in payload
def byte_stuff_overhead(payload):
    framed = byte_stuff_frame(payload)

    return ((len(framed) - len(payload)) / len(payload))*100 + 200 / len(payload)


# return overhead caused by bit stuffing
def bit_stuff_overhead(payload):
    stuffed, bit_len = bit_stuff(payload)

    orig_bits = len(payload) * 8

    return ((bit_len - orig_bits) / orig_bits) * 100

# -------------------------------------------------
# test cases
# -------------------------------------------------

def test_part_a():

    print("\n" + "-" * 60)
    print("PART A - BYTE COUNT FRAMING")
    print("-" * 60)

    payload1 = [0x11, 0x22, 0x33]
    payload2 = [0xAA]

    payloads = [payload1, payload2]

    # Build stream
    stream = byte_count_stream(payloads)

    print("Original payloads:")
    print("Frame 1:", hex_bytes(payload1))
    print("Frame 2:", hex_bytes(payload2))

    print("\nGenerated stream:")
    print(hex_bytes(stream))

    expected = [0x03, 0x11, 0x22, 0x33, 0x01, 0xAA]

    print("\nExpected:")
    print(hex_bytes(expected))

    print("Match:", stream == expected)

    # Clean transmission
    recv = transmit(stream, [])

    recovered = byte_count_parse(recv)

    print("\nClean delivery:")

    for i, payload in enumerate(recovered, 1):
        print(f"Recovered frame {i}:", hex_bytes(payload))

    # Corrupted first count byte
    currpt = transmit(stream,[(0, 0x05)])

    print("\nCorrupted delivery:")
    print(hex_bytes(currpt))

    recovered_corrupted = byte_count_parse(currpt)

    print("\nReceiver output after corruption:")

    for i, payload in enumerate(recovered_corrupted, 1):
        print(f"Recovered frame {i}:", hex_bytes(payload))

    print("\nReason:")
    print("The first count changes from 03 to 05.")
    print("The receiver therefore reads 5 bytes as the first payload.")
    print("This consumes the count byte of the second frame.")
    print("Therefore the receiver loses synchronization.")

def test_part_b():

    print("\n" + "-" * 60)
    print("PART B - BYTE STUFFING")
    print("-" * 60)

    tests = [
        [0x11, 0x22],
        [0x7E],
        [0x7D],
        [0x7D, 0x7E]
    ]

    for payload in tests:

        frame = byte_stuff_frame(payload)

        recv = transmit(frame, [])

        recovered = byte_stuff_deframe(recv)

        print("\nPayload:")
        print(hex_bytes(payload))

        print("Stuffed frame:")
        print(hex_bytes(frame))

        print("Recovered:")
        print(hex_bytes(recovered))

        print("Correct:", recovered == payload)

def test_part_c():

    print("\n" + "-" * 60)
    print("PART C - BIT STUFFING")
    print("-" * 60)

    tests = [
        [0xFF],
        [0x7E],
        [0xFF, 0xFF]
    ]

    for payload in tests:

        stuffed, bit_length = bit_stuff(payload)

        recovered = bit_unstuff(
            stuffed,
            bit_length
        )

        print("\nPayload:")
        print(hex_bytes(payload))

        print("Stuffed bytes:")
        print(hex_bytes(stuffed))

        print("Bit length:")
        print(bit_length)

        print("Recovered:")
        print(hex_bytes(recovered))

        print("Correct:", recovered == payload)

# -------------------------------------------------
# overhead analysis
# -------------------------------------------------

def overhead_analysis():

    print("\n" + "-" * 60)
    print("PART D - OVERHEAD ANALYSIS")
    print("-" * 60)

    # Random data
    random_data = [
        random.randint(0, 255)
        for _ in range(100)
    ]

    # Worst case for byte stuffing: every byte is FLAG
    worst_byte = [FLAG] * 100

    # Worst case for bit stuffing: every bit is 1
    worst_bit = [0xFF] * 100

    print("\nRandom data - 100 bytes")
    print("Byte count overhead:",byte_count_overhead(random_data),"%")
    print("Byte stuffing overhead:",byte_stuff_overhead(random_data),"%")
    print("Bit stuffing overhead:",bit_stuff_overhead(random_data),"%")
    print("Byte count overhead:",byte_count_overhead(worst_byte),"%")
    print("Byte stuffing overhead:",byte_stuff_overhead(worst_byte),"%")
    print("Bit stuffing overhead:",bit_stuff_overhead(worst_bit),"%")

#-----------------------------------------
# main function 
#-----------------------------------------

def main():
    test_part_a()

    test_part_b()

    test_part_c()

    overhead_analysis()

if __name__ == "__main__":
    main()
