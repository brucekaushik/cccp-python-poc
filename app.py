import hashlib
from cccp.codec.encoders import AsciiToJsonIr, JsonIrToBin
from cccp.codec.decoders import BinToJsonIr, JsonIrToAscii

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

if __name__ == "__main__":

    # STAGE1: text -> IR -> full binary -> IR -> text

    input_filepath = 'input_output/input2.txt'
    ir_encoder = AsciiToJsonIr(input_filepath)

    ir_output_filepath = 'input_output/input2_ir1.json'
    ir_encoder.add_header("Knolbay:Poc1@1.0.0")
    ir_encoder.encode()
    ir_encoder.write_ir_to_file(ir_output_filepath)
    ir = ir_encoder.get_ir()

    bin_output_filepath = "input_output/input2_bin1.cccp"
    bin_encoder = JsonIrToBin()
    bin_encoder.set_ir(ir)
    bin_encoder.encode_and_write(bin_output_filepath)

    ir_rec_output_filepath = "input_output/input2_ir1_rec.json"
    bin_decoder = BinToJsonIr(bin_output_filepath)
    bin_decoder.decode_and_write(ir_rec_output_filepath)

    output_filepath = "input_output/input2_rec1.txt"
    json_decoder = JsonIrToAscii()
    json_decoder.set_ir(ir)
    json_decoder.decode_and_write(output_filepath)

    assert md5(ir_output_filepath) == md5(ir_rec_output_filepath)
    assert md5(input_filepath) == md5(output_filepath)

    # STAGE2: IR -> full binary -> IR -> text
    # using the same ir_encoder object and therefore the same ir object from stage1 to further encode
    # but please note that we could use a different ir_encoder object and load the ir json from file

    ir_output_filepath = 'input_output/input2_ir2.json'
    ir_encoder.add_header("Knolbay:Poc2@1.0.0")
    ir_encoder.encode()
    ir_encoder.write_ir_to_file(ir_output_filepath)
    ir = ir_encoder.get_ir()

    bin_output_filepath = "input_output/input2_bin2.cccp"
    bin_encoder = JsonIrToBin()
    bin_encoder.set_ir(ir)
    bin_encoder.encode_and_write(bin_output_filepath)

    ir_rec_output_filepath = "input_output/input2_ir2_rec.json"
    bin_decoder = BinToJsonIr(bin_output_filepath)
    bin_decoder.decode_and_write(ir_rec_output_filepath)

    output_filepath = "input_output/input2_rec2.txt"
    json_decoder = JsonIrToAscii()
    json_decoder.set_ir(ir)
    json_decoder.decode_and_write(output_filepath)

    assert md5(ir_output_filepath) == md5(ir_rec_output_filepath)
    assert md5(input_filepath) == md5(output_filepath)
