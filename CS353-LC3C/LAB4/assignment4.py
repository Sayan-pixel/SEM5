# Task A: Hamming Code Encoder & Decoder (Even Parity, 1-Indexed)

def calculate_redundant_bits(m: int) -> int:
    '''smallest r s.t. 2^r >= m + r + 1'''
    r = 0
    while(1 << r) < (m + r + 1):
        r += 1
    return r

def hamming_encode(data_bits: str) -> str:
    m = len(data_bits)
    r = calculate_redundant_bits(m)
    n = m + r

    codeword = ['0'] * (n + 1)

    data_idx = 0
    for pos in range(1, n + 1):
        if (pos & (pos - 1)) != 0:
            codeword[pos] = data_bits[data_idx]
            data_idx += 1

    # Calculate parity bits (Even Parity)
    for p in range(r):
        parity_pos = 1 << p
        ones_count = 0
        for pos in range(1, n + 1):
            if (pos & parity_pos) != 0 and pos != parity_pos:
                if codeword[pos] == '1':
                    ones_count += 1
        codeword[parity_pos] = '1' if (ones_count % 2 != 0) else '0'

    encoded_str = "".join(codeword[1:])
    return encoded_str


def hamming_decode(codeword: str) -> tuple[str, int, str]:
# returns (corrected_codeword, syndrome, recovered_data)
    n = len(codeword)
    cw_arr = ['0'] + list(codeword) # 1-indexed

    syndrome = 0
    p = 0
    while (1 << p) <= n:
        parity_pos = 1 << p
        ones_count = 0
        for pos in range(1, n + 1):
            if (pos & parity_pos) != 0:
                if cw_arr[pos] == '1':
                    ones_count += 1
        if ones_count % 2 != 0:
            syndrome += parity_pos
        p += 1

    # Correct error if present
    corrected = list(cw_arr)
    if syndrome != 0:
        if syndrome <= n:
            corrected[syndrome] = '0' if corrected[syndrome] == '1' else '1'
    
    corrected_codeword = "".join(corrected[1:])

    # Recover original data bits
    recovered_data = []
    for pos in range(1, n + 1):
        if (pos & (pos - 1)) != 0:
            recovered_data.append(corrected[pos])

    return corrected_codeword, syndrome, "".join(recovered_data)

# Task B: CRC Generator & Checker (Modulo-2 Binary Division)

def modulo2_divide(dividend: str, divisor: str) -> str:
    # Performs bitwise modulo-2 XOR division and returns the remainder.
    div_len = len(divisor)
    cur = list(dividend)

    for i in range(len(dividend) - div_len + 1):
        if cur[i] == '1':
            for j in range(div_len):
                cur[i + j] = '0' if cur[i + j] == divisor[j] else '1'

    remainder = "".join(cur[-(div_len - 1):])
    return remainder

def crc_encode(message_bits: str, generator_bits: str) -> tuple[str, str]:
    k = len(generator_bits) - 1
    padded_message = message_bits + ('0' * k)
    remainder = modulo2_divide(padded_message, generator_bits)
    transmitted_frame = message_bits + remainder
    return transmitted_frame, remainder


def crc_check(received_bits: str, generator_bits: str) -> tuple[str, bool]:
    remainder = modulo2_divide(received_bits, generator_bits)
    is_accepted = (int(remainder, 2) == 0) if remainder else True
    return remainder, is_accepted

# ==================================================
def run_tests():
    print("=" * 60)
    print("TASK A: HAMMING CODE TEST (Test Vector from PDF)")
    print("=" * 60)
    data = "11001010"
    encoded = hamming_encode(data)
    print(f"Data: {data}")
    print(f"Encoded Hamming codeword ({len(encoded)} bits): {encoded}")

    # Induce single-bit error at position 7 (1-indexed)
    rec_list = list(encoded)
    flip_pos = 7
    rec_list[flip_pos - 1] = '1' if rec_list[flip_pos - 1] == '0' else '0'
    received = "".join(rec_list)
    print(f"Received (with induced error at pos {flip_pos}): {received}")

    corrected, syn, rec_data = hamming_decode(received)
    print(f"Syndrome = {syn} -> error at position {syn}")
    print(f"Corrected codeword: {corrected}")
    print(f"Recovered data:     {rec_data}")
    print(f"Verification Success: {rec_data == data and syn == flip_pos}")

    print("\n" + "=" * 60)
    print("TASK B: CRC TEST (Test Vector from PDF)")
    print("=" * 60)
    msg = "1010111"
    gen = "1001"
    frame, rem = crc_encode(msg, gen)
    print(f"Message: {msg}")
    print(f"Generator: {gen}")
    print(f"CRC remainder: {rem} | Transmitted frame: {frame}")

    # Check Clean Frame
    clean_rem, clean_ok = crc_check(frame, gen)
    print(f"Receiver check on clean frame -> remainder {clean_rem} -> {'ACCEPT' if clean_ok else 'REJECT'}")

    # Corrupt one bit (e.g., flip bit at index 2)
    corrupted_frame = list(frame)
    corrupted_frame[2] = '0' if corrupted_frame[2] == '1' else '1'
    corrupted_frame = "".join(corrupted_frame)

    corrupt_rem, corrupt_ok = crc_check(corrupted_frame, gen)
    print(f"Receiver check on corrupted frame ({corrupted_frame}) -> remainder {corrupt_rem} -> {'ACCEPT' if corrupt_ok else 'REJECT'}")

if __name__ == "__main__":
    run_tests()