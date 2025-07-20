from cccp.codec.packers import AsciiToJsonIr

if __name__ == "__main__":

    input_filepath = 'input_output/input2.txt'
    packer = AsciiToJsonIr(input_filepath)

    output_filepath = 'input_output/input2_ir1.json'
    packer.add_header("Knolbay:Poc1@1.0.0")
    packer.encode()
    packer.write_ir_to_file(output_filepath)

    output_filepath = 'input_output/input2_ir2.json'
    packer.add_header("Knolbay:Poc2@1.0.0")
    packer.encode()
    packer.write_ir_to_file(output_filepath)
