import base64

class Representation:

    def validate_binstr(self, binstr):
        return set(binstr) <= {'0', '1'}

    def binstr_to_b64(self, binstr: str, validate: bool = True) -> tuple[str, int]:
        if validate and not self.validate_binstr(binstr):
            raise ValueError("payload contains characters other than '0' or '1'")

        padded_len = (8 - len(binstr) % 8) % 8 # pad to full bytes
        binstr_padded = '0' * padded_len + binstr
        byte_data = int(binstr_padded, 2).to_bytes(len(binstr_padded) // 8, byteorder='big')

        # return base64 + original bit length (not padded length)
        return base64.b64encode(byte_data).decode('ascii'), len(binstr)

    def b64_to_binstr(self, b64_str: str, bit_length: int) -> str:
        byte_data = base64.b64decode(b64_str)
        binstr = ''.join(f'{byte:08b}' for byte in byte_data) # convert to binstr
        return binstr[-bit_length:] # trim back to original bit length

    def binstr_to_hex(self, binstr: str, validate: bool = True) -> tuple[str, int]:
        if validate and not self.validate_binstr(binstr):
            raise ValueError("Input contains characters other than '0' or '1'")

        padded_len = (4 - len(binstr) % 4) % 4 # pad to full nibbles
        binstr = '0' * padded_len + binstr
        hex_str = hex(int(binstr, 2))[2:]  # remove '0x'
        return hex_str, len(binstr) - padded_len  # return hex + actual bit length

    def hex_to_binstr(self, hex_str: str, bit_length: int) -> str:
        binstr = bin(int(hex_str, 16))[2:]  # remove '0b'
        return binstr.zfill(bit_length) # pad to original length

representation = Representation()

if __name__ == '__main__':

    payload = "10111111111111000000000000000110100101100011101000000000000000011100101011110001000000000000000110011101001010000"

    payload_b64, payload_len = representation.binstr_to_b64(payload)
    reconstructed = representation.b64_to_binstr(payload_b64, payload_len)
    assert reconstructed == payload

    payload_hex, payload_len = representation.binstr_to_hex(payload)
    reconstructed = representation.hex_to_binstr(payload_hex, payload_len)
    assert reconstructed == payload
