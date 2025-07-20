import base64
from cccp.codec import bitmath
from cccp.codec.types import PayloadBytesAndSymbolCount

def is_valid_bitstr(bitstr):
    return set(bitstr) <= {'0', '1'}

def bitstr_to_lzb64str(bitstr: str, validate: bool = True) -> tuple[str, int]:
    if validate and not is_valid_bitstr(bitstr):
        raise ValueError("payload contains characters other than '0' or '1'")

    padded_len = (8 - len(bitstr) % 8) % 8 # pad to full bytes
    bitstr_padded = '0' * padded_len + bitstr
    byte_data = int(bitstr_padded, 2).to_bytes(len(bitstr_padded) // 8, byteorder='big')

    # return base64 + original bit length (not padded length)
    return base64.b64encode(byte_data).decode('ascii'), len(bitstr)

def lzb64str_to_bitstr(b64str: str, bitlen: int) -> str:
    byte_data = base64.b64decode(b64str)
    bitstr = ''.join(f'{byte:08b}' for byte in byte_data) # convert to bitstr
    return bitstr[-bitlen:] # trim back to original bit length

def bitstr_to_lzhexstr(bitstr: str, validate: bool = True) -> tuple[str, int]:
    if validate and not is_valid_bitstr(bitstr):
        raise ValueError("Input contains characters other than '0' or '1'")

    padlen = (4 - len(bitstr) % 4) % 4 # pad to full nibbles
    bitstr = '0' * padlen + bitstr
    hex_str = hex(int(bitstr, 2))[2:]  # remove '0x'
    return hex_str, len(bitstr) - padlen  # return hex + actual bit length

def lzhexstr_to_bitstr(lzhexstr: str, bitlen: int) -> str:
    bitstr = bin(int(lzhexstr, 16))[2:]  # remove '0b'
    return bitstr.zfill(bitlen) # pad to original length

def dec_to_bitstr(bit_val: str, bitlen: int) -> str:
    return f"{bit_val:0{bitlen}b}"

def bitstr_to_dec(bitstr: str) -> int:
    return int(bitstr, 2)

def binstr_to_bytes_and_symbol_count(payload_binstr:str, payload_binlen: int, symbol_width: int) -> PayloadBytesAndSymbolCount:
    if payload_binlen == 0 and payload_binstr:
        raise ValueError("If payload_binlen is 0, the payload string must also be empty.")

    if(symbol_width > payload_binlen):
        raise ValueError(f"Symbol width of your LUT ({symbol_width}) is greater than payload bit length ({payload_binlen})")

    if not isinstance(payload_binlen, int) or payload_binlen < 0:
        raise ValueError("payload_binlen must be a non-negative integer.")

    if not is_valid_bitstr(payload_binstr):
        raise ValueError("payload is not a valid binstr as it contains other characters apart from 0 & 1")

    if not isinstance(symbol_width, int) or symbol_width <= 0:
        raise ValueError("symbol_width must be a positive integer.")

    if payload_binlen % symbol_width != 0:
        raise ValueError(f"The payload_binlen ({payload_binlen}) is not perfectly divisible by symbol_width ({symbol_width}).")

    pad_bitlen = bitmath.calculate_byte_padding_bits(payload_binlen)
    total_bits = payload_binlen + pad_bitlen
    total_bytes = total_bits // 8
    payload_bytes = int(payload_binstr, 2).to_bytes(total_bytes, byteorder='big')
    symbol_count = int(payload_binlen / symbol_width)

    return payload_bytes, symbol_count

if __name__ == '__main__':

    payload = "000010111111111111000000000000000110100101100011101000000000000000011100101011110001000000000000000110011101001010000"

    payload_b64, payload_len = bitstr_to_lzb64str(payload)
    reconstructed = lzb64str_to_bitstr(payload_b64, payload_len)
    assert reconstructed == payload

    payload_hex, payload_len = bitstr_to_lzhexstr(payload)
    reconstructed = lzhexstr_to_bitstr(payload_hex, payload_len)
    assert reconstructed == payload

    payload = "00000000000000000000000000000000000010" # 10000000 after padding
    payload_binlen = len(payload)
    symbol_width = 19
    payload_bytes, symbol_count = binstr_to_bytes_and_symbol_count(payload, payload_binlen, symbol_width)
    expected_bytes = int(8).to_bytes(5, byteorder='big')
    assert expected_bytes == payload_bytes
