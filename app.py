from cccp.codec.packers import AsciiToJsonIr

if __name__ == "__main__":

    input_filepath = 'input_output/input2.txt'
    output_filepath = 'input_output/input2_ir.json'
    packer = AsciiToJsonIr(input_filepath)
    packer.add_header("Knolbay:Poc1@1.0.0")
    packer.encode()
    packer.write_ir_to_file(output_filepath)
