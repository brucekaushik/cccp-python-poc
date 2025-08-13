from typing import Dict, Optional, TextIO, cast
from cccp.codec import vendor
from cccp.codec.contracts import BaseJsonIrToAscii
from cccp.codec.context import IrContext
from cccp.codec.types import JsonIrSegment

# NOTE TO MYSELF: this is not performant
# consider keeping cpu hot using mmap, sqlite / fsm, numpy, parallel processing, maybe implement in cython if needed
# avoid using nested luts, gil, context switches (cache misses), file io overhead, defer loading all luts in ram
# consider all this when making cccp itself fully streamable, when using json this approach should be fine

class JsonIrToAscii(IrContext):

    def __init__(self) -> None:
        super().__init__()
        self.unpackers: Dict[str, Optional[BaseJsonIrToAscii]] = {}

    def load_unpackers(self) -> None:
        if not self.lut_meta:
            raise ValueError("Please load the lut_meta for all the headers")

        self.unpackers["H1"] = None
        self.unpackers["H2"] = None
        self.unpackers["H3"] = None

        for header_code, header_data in self.lut_meta.items():
            if header_code in ["H1", "H2", "H3"]:
                continue
            vendor_sign = header_data["sign"]
            unpacker = vendor.get_JsonIrToAscii_obj(vendor_sign)
            self.unpackers[header_code] = unpacker

    def write_segments(self, fp: TextIO):
        for segment in self.ir["segments"]:

            if segment[0] == "H1":
                ascii_text = self.get_text_of_exclude_segment(segment)
                fp.write(ascii_text)
            elif segment[0] == "H2":
                ascii_text = self.get_text_of_newline_segment(segment)
                fp.write(ascii_text)
            else:
                ascii_text = self.get_text_of_vendor_segment(segment)
                fp.write(ascii_text)

    def get_text_of_exclude_segment(self, segment: JsonIrSegment) -> str:
        header_code = cast(str, segment[0])
        payload_bitlen = cast(int, segment[1])
        payload = cast(str, segment[2])

        return payload

    def get_text_of_newline_segment(self, segment: JsonIrSegment) -> str:
        header_code = cast(str, segment[0])
        payload_bitlen = cast(int, segment[1])
        payload = cast(str, segment[2])

        return payload

    def get_text_of_vendor_segment(self, segment: JsonIrSegment) -> str:
        header_code = cast(str, segment[0])
        payload_bitlen = cast(int, segment[1])
        payload = cast(str, segment[2])

        vendor_unpacker = cast(BaseJsonIrToAscii, self.unpackers[header_code])
        vendor_lut_meta = self.lut_meta[header_code]
        vendor_lut = self.luts[header_code]

        payload = vendor_unpacker.decode_segment(payload_bitlen, payload, vendor_lut_meta, vendor_lut)

        return payload

    def decode_and_write(self, ascii_filepath: str) -> None:
        self.set_lut_meta_for_default_headers()
        self.load_lut_meta()
        self.load_luts(reversed=True)
        self.load_unpackers()

        with open(ascii_filepath, 'a') as fp:
            fp.truncate(0)
            self.write_segments(fp)
