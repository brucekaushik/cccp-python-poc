import os
import json
import re
import pprint
from typing import Dict, List, Union, Optional, cast
from pathlib import Path
from io import BufferedReader
from cccp.codec.types import JsonIrSegment
from cccp.codec.contracts import BaseBinToJsonIr
from cccp.codec import vendor
from cccp.codec.context import IrContext

class BinToJsonIr(IrContext):
    # TODO: consider using sqlite to load 1 lut at a time and keep cpu hot with no cache misses,
    # or maybe give an option to choose, or maybe a different decoder class

    def __init__(self, bin_filepath: str) -> None:
        super().__init__()
        self.bin_filepath: str = bin_filepath
        self.decoders: Dict[str, Optional[BaseBinToJsonIr]] = {}

    def load_decoders(self) -> None:
        if not self.lut_meta:
            raise ValueError("Please load the lut_meta for all the headers")

        self.decoders["H1"] = None
        self.decoders["H2"] = None
        self.decoders["H3"] = None

        for header_code, header_data in self.lut_meta.items():
            if header_code in ["H1", "H2", "H3"]:
                continue
            vendor_sign = header_data["sign"]
            decoder = vendor.get_BinToJsonIr_obj(vendor_sign)
            self.decoders[header_code] = decoder

    def decode_file_header(self, fp: BufferedReader) -> None:
        stream_bytes = fp.read(10)
        buffer = stream_bytes.decode('ascii').strip()

        if not re.match(r'^CCCP\d+\.\d+\.\d+', buffer):
            raise ValueError("Expectation Failure: Invalid file header, expected CCCP version header")

        buffer = buffer.strip('CCCP')
        self.ir["version"] = buffer

    def decode_segment_headers(self, fp: BufferedReader) -> None:
        header_data = []
        header_buffer = ""

        while True:
            stream_bytes = fp.read(1)
            char = stream_bytes.decode('ascii')

            if not char:
                raise ValueError("Expectation Failure: headers are not terminated by $")

            if char not in ["\n", ",", "$"]:
                header_buffer += char
                continue

            if char == ",":
                header_data.append(header_buffer)
                header_buffer = ""
            elif char == "\n":
                header_data.append(header_buffer)
                self.ir["headers"].append(header_data)
                header_buffer = ""
                header_data = []
            elif char == "$":
                break

    def decode_exclude_segment(self, header_code: str, fp: BufferedReader) -> JsonIrSegment:
        buffer = []
        while True:
            stream_byte = fp.read(1)
            if stream_byte != b'\n':
                buffer.append(stream_byte.decode('ascii'))
                continue
            else:
                payload = ''.join(buffer)
                return [header_code, len(buffer) * 8, payload]

    def decode_newline_segment(self, header_code: str, fp: BufferedReader) -> JsonIrSegment:
        return [header_code, 8, "\n"]

    def decode_vendor_segment(self, header_code: str, fp: BufferedReader) -> JsonIrSegment:

        symbol_width = self.lut_meta[header_code]["symbol_width"]
        scheme = cast(str, self.lut_meta[header_code]["scheme"])
        sign = self.lut_meta[header_code]["sign"]
        decoder = cast(BaseBinToJsonIr, self.decoders[header_code])
        payload_bitlen, payload_str = decoder.decode_segment(fp, symbol_width, scheme)

        return [header_code, payload_bitlen, payload_str]

    def decode_segments(self, fp: BufferedReader) -> None:
        current_header = None

        while True:
            stream_byte = fp.read(1)

            if not stream_byte:
                break

            if stream_byte == b'\x01':
                current_header = "H1"
                segment = self.decode_exclude_segment(current_header, fp)
                self.ir["segments"].append(segment)

            elif stream_byte == b'\x02':
                current_header = "H2"
                segment = self.decode_newline_segment(current_header, fp)
                self.ir["segments"].append(segment)

            else:
                current_header = 'H' + str(int.from_bytes(stream_byte, 'big'))
                segment = self.decode_vendor_segment(current_header, fp)
                self.ir["segments"].append(segment)

    def decode_and_write(self, ir_filepath: str) -> None:
        self.set_lut_meta_for_default_headers()

        with open(self.bin_filepath, 'rb') as fp:
            self.decode_file_header(fp)
            self.decode_segment_headers(fp)
            self.load_lut_meta()
            self.load_decoders()
            self.decode_segments(fp)

        with open(ir_filepath, 'w') as fp:
            json.dump(self.ir, fp, indent=4)
