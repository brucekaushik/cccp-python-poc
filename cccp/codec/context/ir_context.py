import json
from pathlib import Path
from typing import List, Dict, Union, TypedDict, Optional
from cccp.codec.types import JsonIr, VendorLutMetaDict, VendorLutDict
from cccp.codec import vendor


class IrContext():

    def __init__(self) -> None:
        self.ir: JsonIr = self.init_ir()
        self.luts: Dict[str, VendorLutDict] = {}
        self.lut_meta: Dict[str, VendorLutMetaDict] = {}
        self.default_header_count: int = 3
        self.last_header_num: int = 3
        self.last_header_code: str = "H3"

    def init_ir(self) -> JsonIr:
        ir: JsonIr = {
            "version": "0.0.1",
            "headers": [
                ["H1", "Exclude"],
                ["H2", "NewLine"],
                ["H3", "ContinueousSpaces"],
            ],
            "segments": [],
        }
        return ir

    def get_ir(self) -> JsonIr:
        return self.ir

    # TODO: this is not applicable when unpacking, maybe move this elsewhere
    def load_ir_from_file(self, ir_filepath) -> None:
        with open(ir_filepath, 'r') as fp:
            self.ir = json.load(fp)

    # TODO: this is not applicable when unpacking, maybe move this elsewhere
    def set_ir(self, ir: JsonIr) -> None:
        self.ir = ir

    def write_ir_to_file(self, output_filepath: str) -> None:
        with open(output_filepath, 'w') as fp:
            json.dump(self.ir, fp, indent=4)

    def set_lut_meta_for_default_headers(self) -> None:
        if self.lut_meta:
            return

        self.lut_meta["H1"] = {
            "byte": 0b00000001,
            "name": "Exclude",
            "symbol_width": 0,
            "scheme": None,
            "sign": "Exclude",
        }
        self.lut_meta["H2"] = {
            "byte": 0b00000010,
            "name": "NewLine",
            "symbol_width": 0,
            "scheme": None,
            "sign": "NewLine",
        }
        self.lut_meta["H3"] = {
            "byte": 0b00000011,
            "name": "ContinueousSpaces",
            "symbol_width": 0,
            "scheme": None,
            "sign": "ContinueousSpaces",
        }

    # TODO: this is not applicable when unpacking, maybe move this elsewhere
    def add_header(self, header_name: str) -> None:
        self.last_header_num += 1
        self.last_header_code = f"H{self.last_header_num}"
        vendor.validate_sign(header_name)
        self.ir["headers"].append([self.last_header_code, header_name])

    def load_lut_meta(self) -> None:
        for segment_header in self.ir['headers']:
            if segment_header[0] in ["H1", "H2", "H3"]:
                continue

            header_code = segment_header[0]
            header_name = segment_header[1]

            if header_code in self.lut_meta:
                continue

            self.load_header_lut_meta(header_name, header_code)

    def load_header_lut_meta(self, header_name: str, header_code: str):
        vendor_package_path = vendor.get_vendor_package_path(header_name)
        lut_meta_path = vendor_package_path / "lut_meta.json"

        with open(lut_meta_path, 'r') as f:
            data = json.load(f)
            self.lut_meta[header_code] = data
            self.lut_meta[header_code]["byte"] = int(header_code.strip('H'))

    def load_luts(self, reversed: bool = False) -> None:
        for segment_header in self.ir['headers']:
            if segment_header[0] in ["H1", "H2", "H3"]:
                continue

            header_code = segment_header[0]
            header_name = segment_header[1]

            if header_code in self.luts:
                continue

            self.load_header_lut(header_name, header_code, reversed)

    def load_header_lut(self, header_name: str, header_code: str, reversed: bool = False):
        vendor_package_path = vendor.get_vendor_package_path(header_name)
        lut_path = vendor_package_path / "lut_map.json"

        with open(lut_path, 'r') as f:
            data = json.load(f)
            if reversed:
                data = {v: k for k, v in data.items()}
            self.luts[header_code] = data
