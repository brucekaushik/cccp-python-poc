import json
import pprint
from io import BufferedWriter
from typing import List, Dict, Optional, Union
from cccp.codec.types import JsonIrSegment
from cccp.codec.context import IrContext
from cccp.codec.contracts import BaseJsonIrToBin
from cccp.codec import vendor


class JsonIrToBin(IrContext):

    def __init__(self) -> None:
        super().__init__()
        self.packers: Dict[str, BaseJsonIrToBin] = {}

    def load_packers(self):
        if not self.lut_meta:
            raise ValueError("Please load the lut_meta for all the headers")

        self.packers["H1"] = None
        self.packers["H2"] = None
        self.packers["H3"] = None

        for header_code, header_data in self.lut_meta.items():
            if header_code in ["H1", "H2", "H3"]:
                continue
            vendor_sign = header_data["sign"]
            packer = vendor.get_JsonIrToBin_obj(vendor_sign)
            self.packers[header_code] = packer

    def write_file_header(self, fp: BufferedWriter) -> None:
        header = f"CCCP{self.ir['version']}\n"
        fp.write(header.encode('ascii'))

    def write_segment_headers(self, fp: BufferedWriter) -> None:
        for segment_header in self.ir['headers']:
            if segment_header[0] in ["H1", "H2", "H3"]:
                continue
            bin_bytes = f"{segment_header[0]},{segment_header[1]}\n".encode('ascii')
            fp.write(bin_bytes)

    def write_end_of_headers(self, fp: BufferedWriter) -> None:
        fp.write('$'.encode('ascii'))

    def get_bytes_of_exclude_segment(self, segment: JsonIrSegment) -> bytes:
        header_code = segment[0]
        payload_bitlen = segment[1]
        payload = segment[2]

        header_byte = self.lut_meta[header_code]["byte"].to_bytes(1, byteorder='big')
        payload_bytes = payload.encode('ascii')
        newline_byte = "\n".encode('ascii')
        segment_bytes = b''.join([header_byte, payload_bytes, newline_byte])

        return segment_bytes

    def get_bytes_of_newline_segment(self, segment: JsonIrSegment) -> bytes:
        header_code = segment[0]
        header_byte = self.lut_meta[header_code]["byte"].to_bytes(1, byteorder='big')
        return header_byte

    def get_bytes_of_vendor_segment(self, segment: JsonIrSegment) -> bytes:
        header_code = segment[0]
        header_byte = self.lut_meta[header_code]["byte"].to_bytes(1, byteorder='big')
        scheme = self.lut_meta[header_code]["scheme"]
        symbol_width = self.lut_meta[header_code]["symbol_width"]

        packer = self.packers[header_code]
        vendor_byte_list = packer.get_bytes_of_segment(segment, scheme, symbol_width)
        return b"".join([header_byte] + vendor_byte_list)

    def write_segments(self, fp: BufferedWriter) -> None:
        for segment in self.ir["segments"]:
            if segment[0] == "H1":
                segment_bytes = self.get_bytes_of_exclude_segment(segment)
                fp.write(segment_bytes)
            elif segment[0] == "H2":
                segment_bytes = self.get_bytes_of_newline_segment(segment)
                fp.write(segment_bytes)
            else:
                segment_bytes = self.get_bytes_of_vendor_segment(segment)
                fp.write(segment_bytes)

    def encode_and_write(self, bin_filepath: str) -> None:
        self.set_lut_meta_for_default_headers()
        self.load_lut_meta()
        self.load_packers()

        with open(bin_filepath, 'ab') as fp:
            fp.truncate(0)
            self.write_file_header(fp)
            self.write_segment_headers(fp)
            self.write_end_of_headers(fp)
            self.write_segments(fp)
