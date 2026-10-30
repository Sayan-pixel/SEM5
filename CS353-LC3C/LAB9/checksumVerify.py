def verify_ip_checksum(header):
    # Extract the stored checksum at bytes 10 and 11
    stored = (header[10] << 8) | header[11]
    
    total = 0
    # Sum the header as 16-bit words, skipping the stored checksum field
    for i in range(0, 20, 2):
        if i == 10:
            continue
        word = (header[i] << 8) | header[i+1]
        total += word
        
    # Fold carries out of 16 bits back in
    while (total >> 16) > 0:
        total = (total & 0xFFFF) + (total >> 16)
        
    # Take the one's complement
    computed = ~total & 0xFFFF
    valid = (stored == computed)
    
    return stored, computed, valid

def reassemble(fragments):
    ranges = []
    total_length = 0
    complete = False
    
    # Calculate byte positions (offset units * 8)
    for offset_units, more_fragments, payload_length in fragments:
        start = offset_units * 8
        end = start + payload_length - 1
        ranges.append((start, end))
        
        # If the more-fragments flag is clear, this is the final piece
        if more_fragments == 0:
            total_length = end + 1
            complete = True
            
    return ranges, total_length, complete

# Inputs provided by the lab instructions
clean_header = bytes.fromhex("45 00 00 28 1C 46 00 00 40 11 DB 10 C0 A8 01 0A C0 A8 01 14")
corrupted_header = bytes.fromhex("45 00 00 28 1C 46 00 00 3F 11 DB 10 C0 A8 01 0A C0 A8 01 14")

# List of fragments: (offset_units, more_fragments_flag, payload_length)
fragment_data = [
    (0, 1, 1480),
    (185, 1, 1480),
    (370, 0, 40)
]

# Execution
clean_stored, clean_computed, clean_valid = verify_ip_checksum(clean_header)
print(f"Clean Header -> Stored: 0x{clean_stored:04X}, Computed: 0x{clean_computed:04X}, Valid: {clean_valid}")

corrupt_stored, corrupt_computed, corrupt_valid = verify_ip_checksum(corrupted_header)
print(f"Corrupted Header -> Stored: 0x{corrupt_stored:04X}, Computed: 0x{corrupt_computed:04X}, Valid: {corrupt_valid}")

ranges, total_len, is_complete = reassemble(fragment_data)
print(f"Fragments -> Ranges: {ranges}, Total Length: {total_len}, Complete: {is_complete}")