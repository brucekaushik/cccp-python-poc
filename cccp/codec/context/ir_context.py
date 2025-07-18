import json
from typing import List, Dict, TypedDict

class JsonIR(TypedDict):
    version: str
    headers: List[List[str]]
    segments: List

class IrContext():

    def __init__(self) -> None:
        self.ir: JsonIR = self.init_ir()

    def init_ir(self) -> JsonIR:
        ir = {
            "version": "0.0.1",
            "headers": [
                ["H1", "Exclude"],
                ["H2", "NewLine"],
                ["H3", "ContinueousSpaces"],
            ],
            "segments": [],
        }
        return ir

    def get_ir(self) -> JsonIR:
        return self.ir

    # TODO: this is not applicable when unpacking, maybe move this elsewhere
    def load_ir_from_file(self, ir_filepath) -> None:
        with open(ir_filepath, 'r') as fp:
            self.ir = json.load(fp)

    # TODO: this is not applicable when unpacking, maybe move this elsewhere
    def set_ir(self, ir: Dict) -> None:
        self.ir = ir

    def write_ir_to_file(self, output_filepath: str) -> None:
        with open(output_filepath, 'w') as fp:
            json.dump(self.ir, fp, indent=4)
