from cccp.codec.packers import AsciiToJsonIr, JsonIrToBin

if __name__ == "__main__":

    input_filepath = 'input_output/input2.txt'
    ir_packer = AsciiToJsonIr(input_filepath)

    output_filepath = 'input_output/input2_ir1.json'
    ir_packer.add_header("Knolbay:Poc1@1.0.0")
    ir_packer.encode()
    ir_packer.write_ir_to_file(output_filepath)
    ir = ir_packer.get_ir()

    bin_filepath = "input_output/input2_bin1.cccp"
    bin_packer = JsonIrToBin()
    bin_packer.set_ir(ir)
    bin_packer.encode_and_write(bin_filepath)

    output_filepath = 'input_output/input2_ir2.json'
    ir_packer.add_header("Knolbay:Poc2@1.0.0")
    ir_packer.encode()
    ir_packer.write_ir_to_file(output_filepath)
    ir = ir_packer.get_ir()

    bin_filepath = "input_output/input2_bin2.cccp"
    bin_packer = JsonIrToBin()
    bin_packer.set_ir(ir)
    bin_packer.encode_and_write(bin_filepath)
