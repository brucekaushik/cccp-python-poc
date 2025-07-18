from typing import List, Optional
from cccp.codec.context import IrContext

class AsciiToJsonIr(IrContext):

    def __init__(self, input_filepath: str) -> None:
        super().__init__()
        self.input_filepath: str = input_filepath

        self.header_code_curr: Optional[str] = None
        self.header_code_prev: Optional[str] = None
        self.unprocessed_chars: List[str] = []

    def encode(self) -> None:
        with open(self.input_filepath, "r", encoding="ascii") as fp:
            while True:
                char = fp.read(1)

                if char == "\n" and self.header_code_prev == "H2":
                    self.conclude_newline_segment()
                    continue
                else:
                    self.header_code_curr = "H1"

                if self.header_code_prev == "H1" and self.header_code_curr != self.header_code_prev and self.unprocessed_chars:
                    self.conclude_ascii_segment()
                    self.reset_payload_data()
                    self.header_code_curr = "H1"

                if char and char != '\n':
                    self.unprocessed_chars.append(char)

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
                elif not char:
                    if self.header_code_curr == "H1" and self.unprocessed_chars:
                        self.conclude_ascii_segment()
                        self.header_code_curr = "H1"
                    break

                self.header_code_prev == self.header_code_curr

    def reset_payload_data(self) -> None:
        self.unprocessed_chars = []

    def conclude_ascii_segment(self) -> None:
        payload_exclude_bitlen = len(self.unprocessed_chars) * 8
        payload_exclude = ''.join(self.unprocessed_chars)

        segment = ["H1", payload_exclude_bitlen, payload_exclude]
        self.ir["segments"].append(segment)

    def conclude_newline_segment(self) -> None:
        segment = ["H2", 8, "\n"]
        self.ir["segments"].append(segment)
