import sys
from io import BufferedReader

# path appended to recognize the cccp package
# this should be ideally be installed as a package from pypi
# or maybe even a just a cccp-utils package
sys.path.append('../../../..')

from typing import Tuple
from cccp.codec import transformers as rep
from cccp.codec import bitmath
from cccp.codec.contracts import BaseBinToJsonIr

class BinToJsonIr(BaseBinToJsonIr):

    def decode_segment(self, fp: BufferedReader, symbol_width: int, scheme: str) -> Tuple[str, int]:

        # TODO: handle EOF? what if the encoder forgot to use a comma for separator?
        symbol_count_str = ''
        while True:
            stream_byte = fp.read(1)
            char = stream_byte.decode('ascii')
            if char == ',':
                break
            symbol_count_str += char

        symbol_count = int(symbol_count_str)
        payload_bitlen = symbol_count * symbol_width
        pad_bitlen = bitmath.calculate_byte_padding_bits(payload_bitlen)
        bytes_to_read = (payload_bitlen + pad_bitlen) // 8

        payload_bytes_padded = fp.read(bytes_to_read)
        payload_bytes_padded_int = int.from_bytes(payload_bytes_padded, byteorder='big')
        payload_str = rep.dec_to_bitstr(payload_bytes_padded_int, payload_bitlen)

        if scheme == "lzb64":
            payload_str, pbl = rep.bitstr_to_lzb64str(payload_str)

        return [payload_bitlen, payload_str]
