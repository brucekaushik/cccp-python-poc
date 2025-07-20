import hashlib
from cccp.codec.packers import AsciiToJsonIr, JsonIrToBin
from cccp.codec.unpackers import BinToJsonIr

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

if __name__ == "__main__":

    input_filepath = 'input_output/input2.txt'
    ir_packer = AsciiToJsonIr(input_filepath)

    ir_output_filepath = 'input_output/input2_ir1.json'
    ir_packer.add_header("Knolbay:Poc1@1.0.0")
    ir_packer.encode()
    ir_packer.write_ir_to_file(ir_output_filepath)
    ir = ir_packer.get_ir()

    bin_output_filepath = "input_output/input2_bin1.cccp"
    bin_packer = JsonIrToBin()
    bin_packer.set_ir(ir)
    bin_packer.encode_and_write(bin_output_filepath)

    ir_rec_output_filepath = "input_output/input2_ir1_rec.json"
    bin_unpacker = BinToJsonIr(bin_output_filepath)
    bin_unpacker.decode_and_write(ir_rec_output_filepath)

    assert md5(ir_output_filepath) == md5(ir_rec_output_filepath)

    ir_output_filepath = 'input_output/input2_ir2.json'
    ir_packer.add_header("Knolbay:Poc2@1.0.0")
    ir_packer.encode()
    ir_packer.write_ir_to_file(ir_output_filepath)
    ir = ir_packer.get_ir()

    bin_output_filepath = "input_output/input2_bin2.cccp"
    bin_packer = JsonIrToBin()
    bin_packer.set_ir(ir)
    bin_packer.encode_and_write(bin_output_filepath)

    ir_rec_output_filepath = "input_output/input2_ir2_rec.json"
    bin_unpacker = BinToJsonIr(bin_output_filepath)
    bin_unpacker.decode_and_write(ir_rec_output_filepath)

    assert md5(ir_output_filepath) == md5(ir_rec_output_filepath)
