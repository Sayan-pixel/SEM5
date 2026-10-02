# Name    : SAYAN SHIT
# Roll No : 2401179

def decode_80211(hexstr):
    hexstr = hexstr.replace(" ", "").strip()
    if len(hexstr) < 20:    
        return {"error": "input too short"}
        
    b = bytes.fromhex(hexstr)
    
    fc0 = b[0]
    fc1 = b[1]
    
    protocol_version = fc0 & 0b00000011
    type_val = (fc0 & 0b00001100) >> 2
    subtype_val = (fc0 & 0b11110000) >> 4
    
    type_dict = {0: "Management", 1: "Control", 2: "Data"}
    type_name = type_dict.get(type_val, "Reserved")
    
    subtype_name = str(subtype_val)
    if type_val == 1:
        if subtype_val == 11: subtype_name = "RTS"
        elif subtype_val == 12: subtype_name = "CTS"
        elif subtype_val == 13: subtype_name = "ACK"
    elif type_val == 2:
        if subtype_val == 0: subtype_name = "Data"
        
    tods = (fc1 & 0b00000001)
    fromds = (fc1 & 0b00000010) >> 1
    more_frag = (fc1 & 0b00000100) >> 2
    retry = (fc1 & 0b00001000) >> 3
    power_mgmt = (fc1 & 0b00010000) >> 4
    more_data = (fc1 & 0b00100000) >> 5
    protected = (fc1 & 0b01000000) >> 6
    order = (fc1 & 0b10000000) >> 7
    
    flags = []
    if tods: flags.append("ToDS")
    if fromds: flags.append("FromDS")
    if more_frag: flags.append("More Frag")
    if retry: flags.append("Retry")
    if power_mgmt: flags.append("Power Mgmt")
    if more_data: flags.append("More Data")
    if protected: flags.append("Protected")
    if order: flags.append("Order")
    
    duration = int.from_bytes(b[2:4], byteorder='little')
    
    res = {
        "type": type_name,
        "subtype": subtype_name,
        "flags": flags,
        "duration": duration,
        "addresses": {}
    }
    
    def mac_str(mac_bytes):
        return ":".join(f"{x:02x}" for x in mac_bytes)
        
    offset = 4
    if type_name == "Control":
        if subtype_name == "RTS":
            if len(b) < 16: return {"error": "input too short"}
            res["addresses"]["RA"] = mac_str(b[4:10])
            res["addresses"]["TA"] = mac_str(b[10:16])
        elif subtype_name in ["CTS", "ACK"]:
            if len(b) < 10: return {"error": "input too short"}
            res["addresses"]["RA"] = mac_str(b[4:10])
    elif type_name == "Data":
        if len(b) < 24: return {"error": "input too short"}
        a1 = mac_str(b[4:10])
        a2 = mac_str(b[10:16])
        a3 = mac_str(b[16:22])
        
        seq_ctrl = int.from_bytes(b[22:24], byteorder='little')
        frag_no = seq_ctrl & 0x000F
        seq_no = (seq_ctrl & 0xFFF0) >> 4
        res["fragment_number"] = frag_no
        res["sequence_number"] = seq_no
        
        offset = 24
        
        if tods == 0 and fromds == 0:
            res["addresses"]["DA"] = a1
            res["addresses"]["SA"] = a2
            res["addresses"]["BSSID"] = a3
        elif tods == 1 and fromds == 0:
            res["addresses"]["BSSID"] = a1
            res["addresses"]["SA"] = a2
            res["addresses"]["DA"] = a3
        elif tods == 0 and fromds == 1:
            res["addresses"]["DA"] = a1
            res["addresses"]["BSSID"] = a2
            res["addresses"]["SA"] = a3
        elif tods == 1 and fromds == 1:
            if len(b) < 30: return {"error": "input too short"}
            res["addresses"]["RA"] = a1
            res["addresses"]["TA"] = a2
            res["addresses"]["DA"] = a3
            a4 = mac_str(b[24:30])
            res["addresses"]["SA"] = a4
            offset = 30
            
        if len(b) >= offset + 8:
            llc_snap = b[offset:offset+8]
            if llc_snap.startswith(bytes.fromhex("aaaa03")):
                ethertype = int.from_bytes(llc_snap[6:8], byteorder='big')
                res["ethertype"] = f"0x{ethertype:04x}"
                
    return res

if __name__ == "__main__":
    frames = {
        "F1": "08 01 2c 00 00 1a 2b 3c 4d 5e a4 83 e7 11 22 33 00 50 56 aa bb cc 30 1d aa aa 03 00 00 00 08 00",
        "F2": "08 0a 2c 00 a4 83 e7 11 22 33 00 1a 2b 3c 4d 5e 00 50 56 aa bb cc 40 1d aa aa 03 00 00 00 08 00",
        "F3": "b4 00 5e 01 00 1a 2b 3c 4d 5e a4 83 e7 11 22 33",
        "F4": "c4 00 44 01 a4 83 e7 11 22 33",
        "F5": "d4 00 00 00 a4 83 e7 11 22 33",
        "F6": "08 07 2c 00 02 11 22 33 44 55 02 66 77 88 99 aa 00 50 56 aa bb cc 51 1d a4 83 e7 11 22 33 aa aa 03 00 00 00 08 00"
    }

    for name, hexstr in frames.items():
        print(f"=== {name} ===")
        res = decode_80211(hexstr)
        if "error" in res:
            print(f"Error: {res['error']}\n")
            continue
            
        print(f"Type/Subtype : {res.get('type')} / {res.get('subtype')}")
        flags = res.get('flags', [])
        print(f"Flags        : {', '.join(flags) if flags else 'None'}")
        print(f"Duration     : {res.get('duration')} µs")
        print("Addresses    :")
        for role, addr in res.get('addresses', {}).items():
            print(f"  - {role}: {addr}")
        if 'sequence_number' in res:
            print(f"Seq / Frag   : {res['sequence_number']} / {res['fragment_number']}")
        if 'ethertype' in res:
            print(f"EtherType    : {res['ethertype']}")
        print()
