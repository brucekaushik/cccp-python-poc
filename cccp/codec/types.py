from typing import List, Tuple, Union, Optional, NamedTuple, TypedDict

class JsonIrSegment(NamedTuple):
    header_code: str
    payload_bitlen: int
    payload: str

class JsonIr(TypedDict):
    version: str
    headers: List[List[str]]
    segments: List[List[Union[str, int]]]

class VendorLutDict(TypedDict):
    key: str
    val: str

class VendorLutMetaDict(TypedDict):
    byte: int
    name: str
    symbol_width: int
    scheme: Optional[str]

class PartiallyProcessedPayloadTuple(NamedTuple):
    processed_bitlen: int
    payload: str
    unprocessed_chars: List[str]

class PayloadBitlenAndPayload(NamedTuple):
    payload_bitlen: int
    payload: str

class PayloadBytesAndSymbolCount(NamedTuple):
    payload_bytes: bytes
    symbol_count: int
