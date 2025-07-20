from abc import ABC, abstractmethod
from typing import Optional, Dict, List
from .types import PartiallyProcessedPayloadTuple, PayloadBitlenAndPayload, JsonIrSegment

class BaseAsciiToJsonIr(ABC):

    @abstractmethod
    def process_char(self, char: str, lut: Dict) -> Optional[PartiallyProcessedPayloadTuple]:
        pass

    @abstractmethod
    def conclude_segment(self, payload_bitlen: int, payload: str, lut_meta: Dict) -> PayloadBitlenAndPayload:
        pass

class BaseJsonIrToBin(ABC):

    @abstractmethod
    def get_bytes_of_segment(self, segment: JsonIrSegment, scheme: Optional[str], symbol_width: int) -> List[bytes]:
        pass
