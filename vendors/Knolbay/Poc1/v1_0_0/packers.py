import sys

# path appended to recognize the cccp package
# this should be ideally be installed as a package from pypi
# or maybe even a just a cccp-utils package
sys.path.append('../../../..')

from copy import copy
from typing import List, Optional, Union
from cccp.codec import transformers
from cccp.codec.types import (
    PartiallyProcessedPayloadTuple,
    PayloadBitlenAndPayload,
    VendorLutDict,
    VendorLutMetaDict,
    JsonIrSegment,
)

class AsciiToJsonIr():

    def __init__(self):
        self.unprocessed_chars: List[str] = []
        self.processed_payload: str = ""

    def handle_newline(self, char: str, lut: VendorLutDict) -> PartiallyProcessedPayloadTuple:
        word = ''.join(self.unprocessed_chars)
        if word in lut:
            self.processed_payload = lut[word]
            unprocessed = ["\n"]
            self.unprocessed_chars = [] # reset
            return len(self.processed_payload), self.processed_payload, unprocessed
        else:
            unprocessed = copy(self.unprocessed_chars)
            self.unprocessed_chars = [] # reset
            self.processed_payload = "" # reset
            return 0, self.processed_payload, unprocessed

    def handle_space(self, char: str, lut: VendorLutDict) -> PartiallyProcessedPayloadTuple:
        word = ''.join(self.unprocessed_chars)
        if word in lut:
            self.processed_payload = lut[word]
            self.unprocessed_chars = [] # reset
            return len(self.processed_payload), self.processed_payload, self.unprocessed_chars
        else:
            self.unprocessed_chars.append(" ")
            unprocessed = copy(self.unprocessed_chars)
            self.unprocessed_chars = [] # reset
            self.processed_payload = "" # reset
            return 0, self.processed_payload, unprocessed

    def handle_eof(self, char: None, lut: VendorLutDict) -> PartiallyProcessedPayloadTuple:
        word = ''.join(self.unprocessed_chars)
        if word in lut:
            self.processed_payload = lut[word]
            self.unprocessed_chars = [] # reset
            return len(self.processed_payload), self.processed_payload, self.unprocessed_chars
        else:
            unprocessed = copy(self.unprocessed_chars)
            self.unprocessed_chars = [] # reset
            self.processed_payload = "" # reset
            return 0, self.processed_payload, unprocessed

    def process_char(self, char: Optional[str], lut: VendorLutDict) -> Union[PartiallyProcessedPayloadTuple, bool]:
        if char == "\n":
            return self.handle_newline(char, lut)
        elif char == " ":
            return self.handle_space(char, lut)
        elif not char:
            return self.handle_eof(char, lut)
        else:
            self.unprocessed_chars.append(char)
            return False

    def conclude_segment(self, payload_bitlen: int, payload: str, lut_meta: VendorLutMetaDict) -> PayloadBitlenAndPayload:
        scheme = lut_meta["scheme"]
        if scheme == "lzb64":
            payload, l = transformers.bitstr_to_lzb64str(payload)
        return payload_bitlen, payload
