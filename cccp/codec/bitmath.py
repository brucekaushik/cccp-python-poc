
def calculate_byte_padding_bits(bitlen: int) -> int:
    return (8 - (bitlen % 8)) % 8
