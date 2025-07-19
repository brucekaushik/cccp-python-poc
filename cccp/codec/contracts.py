from abc import ABC, abstractmethod
from typing import Optional, Dict
from .types import PartiallyProcessedPayloadTuple, PayloadBitlenAndPayload

class BaseAsciiToJsonIr(ABC):

    @abstractmethod
    def process_char(self, char: str, lut: Dict) -> Optional[PartiallyProcessedPayloadTuple]:
        pass

    @abstractmethod
    def conclude_segment(self, payload_bitlen: int, payload: str, lut_meta: Dict) -> PayloadBitlenAndPayload:
        pass
