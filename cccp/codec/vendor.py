import os
import re
from pathlib import Path
import importlib
import inspect
from cccp.codec.contracts import (
    BaseAsciiToJsonIr,
    BaseJsonIrToBin,
    BaseBinToJsonIr,
    BaseJsonIrToAscii,
)


def validate_sign(sign: str) -> None:
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9]+:[a-zA-Z0-9]+@\d+\.\d+\.\d+', sign):
        raise ValueError("Invalid vendor header.")

def get_vendor_module_path(sign: str) -> str:
    module_path = 'vendors.' + sign.replace('.', '_').replace(':', '.').replace('@', '.v')
    return module_path

def get_vendor_package_path(sign: str) -> Path:
    cwd = os.getcwd()
    vendors_path = Path(cwd) / "vendors"
    package_path = vendors_path / sign.replace('.', '_').replace(':', '/').replace('@', '/v')
    return package_path

def get_AsciiToJsonIr_obj(sign:str) -> BaseAsciiToJsonIr:
    module_path = get_vendor_module_path(sign) + '.packers'
    module = None

    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError:
        raise ModuleNotFoundError(f"The module at {module_path} does not exist or is not accessible.")

    if not hasattr(module, 'AsciiToJsonIr'):
        raise AttributeError(f"The module {module_path} does not have a class named 'AsciiToJsonIr'.")

    if not inspect.isclass(module.AsciiToJsonIr):
        raise TypeError(f"The attribute 'AsciiToJsonIr' in module {module_path} is not a class.")

    return module.AsciiToJsonIr()

def get_JsonIrToBin_obj(sign: str) -> BaseJsonIrToBin:
    module_path = get_vendor_module_path(sign) + '.packers'
    module = None

    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError:
        raise ModuleNotFoundError(f"The module at {module_path} does not exist or is not accessible.")

    if not hasattr(module, 'JsonIrToBin'):
        raise AttributeError(f"The module {module_path} does not have a class named 'JsonIrToBin'.")

    if not inspect.isclass(module.JsonIrToBin):
        raise TypeError(f"The attribute 'JsonIrToBin' in module {module_path} is not a class.")

    return module.JsonIrToBin()

def get_BinToJsonIr_obj(sign: str) -> BaseBinToJsonIr:
    module_path = get_vendor_module_path(sign) + '.unpackers'
    module = None

    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError:
        raise ModuleNotFoundError(f"The module at {module_path} does not exist or is not accessible.")

    if not hasattr(module, 'BinToJsonIr'):
        raise AttributeError(f"The module {module_path} does not have a class named 'JsonIrToBin'.")

    if not inspect.isclass(module.BinToJsonIr):
        raise TypeError(f"The attribute 'JsonIrToBin' in module {module_path} is not a class.")

    return module.BinToJsonIr()

def get_JsonIrToAscii_obj(sign: str) -> BaseJsonIrToAscii:
    module_path = get_vendor_module_path(sign) + '.unpackers'
    module = None

    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError:
        raise ModuleNotFoundError(f"The module at {module_path} does not exist or is not accessible.")

    if not hasattr(module, 'JsonIrToAscii'):
        raise AttributeError(f"The module {module_path} does not have a class named 'JsonIrToAscii'.")

    if not inspect.isclass(module.JsonIrToAscii):
        raise TypeError(f"The attribute 'JsonIrToAscii' in module {module_path} is not a class.")

    return module.JsonIrToAscii()
