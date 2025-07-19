from typing import List, Optional
from cccp.codec.context import IrContext
from cccp.codec.contracts import BaseAsciiToJsonIr
from cccp.codec import vendor


class AsciiToJsonIr(IrContext):

    def __init__(self, input_filepath: str) -> None:
        super().__init__()
        self.input_filepath: str = input_filepath

        self.header_code_curr: Optional[str] = None
        self.header_code_prev: Optional[str] = None
        self.unprocessed_chars: List[str] = []
        self.processed_payloads: List[str] = []
        self.processed_payload_bitlens: List[int] = []

        self.vendor_header_code: Optional[str] = None
        self.vendor_sign: Optional[str] = None
        self.vendor_packer: Optional[BaseAsciiToJsonIr] = None

    def load_vendor_data(self):
        self.vendor_header_code = f"H{self.last_header_num}"
        self.vendor_sign = self.lut_meta[self.vendor_header_code]["sign"]
        self.vendor_packer = vendor.get_AsciiToJsonIr_obj(self.vendor_sign)

    def encode(self) -> None:
        self.set_lut_meta_for_default_headers()
        self.load_lut_meta()
        self.load_vendor_data()

        with open(self.input_filepath, "r", encoding="ascii") as fp:
            while True:
                char = fp.read(1)

                if char == "\n" and self.header_code_prev == "H2":
                    self.conclude_newline_segment()
                    continue

                partially_procesed_payload = self.vendor_packer.process_char(char, self.lut)
                if not partially_procesed_payload:
                    continue

                processed_payload_bitlen = partially_procesed_payload[0]
                processed_payload = partially_procesed_payload[1]
                unprocessed_chars = partially_procesed_payload[2]

                if char == "\n" and unprocessed_chars[-1] != "\n":
                    ValueError("Vendors must not process newline character, as the SDK handles it")

                if processed_payload_bitlen != 0:
                    self.header_code_curr = self.vendor_header_code
                elif processed_payload_bitlen == 0 and len(unprocessed_chars) != 0:
                    self.header_code_curr = "H1"
                else:
                    ValueError("Vendors must handle the unprocessed characters properly")

                # TODO: rethink about this..
                if char not in [" ", "\n"]:
                    ValueError("Not expecting the vendor to stop consuming bytes until newline or space")

                if self.header_code_prev == "H1" \
                        and self.header_code_curr != self.header_code_prev \
                        and self.unprocessed_chars:
                    self.conclude_ascii_segment()
                    self.reset_payload_data()
                elif self.header_code_prev == self.vendor_header_code \
                        and self.header_code_curr != self.header_code_prev \
                        and sum(self.processed_payload_bitlens) != 0:
                    self.conclude_vendor_segment()
                    self.reset_payload_data()

                self.unprocessed_chars += unprocessed_chars
                self.processed_payloads.append(processed_payload)
                self.processed_payload_bitlens.append(processed_payload_bitlen)

                if char == "\n":
                    if self.header_code_curr == "H1" and self.unprocessed_chars:
                        self.conclude_ascii_segment()
                        self.conclude_newline_segment()
                        self.reset_payload_data()
                        self.header_code_curr = "H2"
                    elif self.header_code_curr == "H1" and not self.unprocessed_chars:
                        self.conclude_newline_segment()
                        self.reset_payload_data()
                        self.header_code_curr = "H2"
                    elif self.header_code_curr == self.vendor_header_code and sum(self.processed_payload_bitlens) != 0:
                        self.conclude_vendor_segment()
                        self.conclude_newline_segment()
                        self.reset_payload_data()
                        self.header_code_prev = "H2"
                    elif self.header_code_curr == self.vendor_header_code and sum(self.processed_payload_bitlens) == 0:
                        self.conclude_newline_segment()
                        self.reset_payload_data()
                        self.header_code_curr = "H2"
                elif not char:
                    if self.header_code_curr == "H1" and self.unprocessed_chars:
                        self.conclude_ascii_segment()
                    if self.header_code_curr == self.vendor_header_code and sum(self.processed_payload_bitlens) != 0:
                        self.conclude_vendor_segment()
                    break # EOF

                self.header_code_prev = self.header_code_curr

    def reset_payload_data(self) -> None:
        self.unprocessed_chars = []
        self.processed_payloads = []
        self.processed_payload_bitlens = []

    def conclude_ascii_segment(self) -> None:
        payload_exclude_bitlen = len(self.unprocessed_chars) * 8
        payload_exclude = ''.join(self.unprocessed_chars)

        segment = ["H1", payload_exclude_bitlen, payload_exclude]
        self.ir["segments"].append(segment)

    def conclude_newline_segment(self) -> None:
        segment = ["H2", 8, "\n"]
        self.ir["segments"].append(segment)

    def conclude_vendor_segment(self) -> None:
        lut_meta =  self.lut_meta[self.vendor_header_code]
        payload = ''.join(self.processed_payloads)
        payload_bitlen = sum(self.processed_payload_bitlens)

        payload_bitlen, payload = self.vendor_packer.conclude_segment(payload_bitlen, payload, lut_meta)
        segment = [self.vendor_header_code, payload_bitlen, payload]
        self.ir["segments"].append(segment)
