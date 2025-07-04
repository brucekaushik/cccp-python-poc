"""
THIS ENCODER DOES NOT HANDLE THE FOLLOWING PROPERLY YET:
- cross platform line endings
- considers the encoding as ASCII
- EOF behavior
- line buffering
- space like values apart from \s and \n
- leading spaces or space like characters in a line
    - a guideline/rule to be included for the vendors
- does not handle continuous spaces or space like characters
    - a guideline/rule to be included for the vendors
- maybe read file in binary mode, so that the python's 'magic' does not happen
- need to move all these functions to be accessible via an api convenient to use
    - vendors only need to worry about LUTs, not logic as it is hard
- performance
    - reading file bit by bit instead of chunks
    - globals
    - string concatenation (extra memory usage)

and many more considerations / trade-offs like the above..
"""

import json
from cccp import representation

input_filename = 'io/input2.txt'
ir_filename = 'io/input2_ir.json'

with open('lut.json', 'r') as file:
    lut = json.load(file)

ir = {}
ir["version"] = "0.2"
ir["headers"] = {}
ir["headers"]["H1"] = "EXCLUDE"
ir["headers"]["H2"] = "NEWLINE"
ir["headers"]["H3"] = "LUT:KNOLBAY:zoo@1.0"
ir["payload_schema"] = {}
ir["payload_schema"]["H3"] = "lzhex"
ir["segments"] = []

def is_word_in_lut(word):
    return word in lut["map"]

def add_word_binary_to_segment(word):
    binary = lut["map"][word]
    ir["segments"][-1][2] += binary

def add_word_ascii_to_segment(word):
    ir["segments"][-1][2] += word

def add_ascii_space_to_segment():
    ir["segments"][-1][2] += ' '

def add_bin_space_to_segment(char):
    binary = lut["map"][char]
    ir["segments"][-1][2] += binary

def add_new_empty_segment(segment_header):
    ir["segments"].append([segment_header, 0, ""]) # header, PayloadBitLength, payload

def add_new_newline_segment(segment_header, char):
    ir["segments"].append([segment_header, 0, char]) # header, PayloadBitLength, payload

def conclude_segment_b64():
    if not ir["segments"]:
        return
    segment = ir["segments"][-1]
    payload = segment[2]
    payload_b64, payload_len = representation.binstr_to_b64(payload)
    segment[1] = payload_len
    segment[2] = payload_b64
    return payload_b64, payload_len

def conclude_segment_ascii():
    if not ir["segments"]:
        return
    segment = ir["segments"][-1]
    payload_ascii = segment[2]
    payload_len = len(payload_ascii) * 8
    segment[1] = payload_len
    segment[2] = payload_ascii
    return payload_ascii, payload_len

def encode():
    segment_header = None
    prev_segment_header = None
    word = ""

    with open(input_filename, "r", encoding="utf-8") as file:
        i = 0
        while True:
            char = file.read(1)

            if not char and prev_segment_header == "H1":
                conclude_segment_ascii()
                break #EOF

            elif not char and prev_segment_header == "H3":
                conclude_segment_b64()
                break #EOF

            # print('----------------')
            # print(f"[REPR] {repr(char)} (ord: {ord(char)})")

            if not char.isspace():
                word += char
                continue

            elif char.isspace() and char != "\n":

                word_exists_in_lut = is_word_in_lut(word)

                if word_exists_in_lut:
                    segment_header = "H3"
                    if prev_segment_header != segment_header:
                        conclude_segment_ascii()
                        add_new_empty_segment(segment_header)
                    add_word_binary_to_segment(word)
                    add_bin_space_to_segment(char)

                else:
                    segment_header = "H1"
                    if prev_segment_header != segment_header and prev_segment_header != "H2":
                        conclude_segment_b64()
                        add_new_empty_segment(segment_header)
                    if prev_segment_header != segment_header and prev_segment_header == "H2":
                        conclude_segment_ascii()
                        add_new_empty_segment(segment_header)
                    add_word_ascii_to_segment(word)
                    add_ascii_space_to_segment()

                prev_segment_header = segment_header
                word = ""

            elif char.isspace() and char == '\n':

                word_exists_in_lut = is_word_in_lut(word)

                if segment_header == "H3" and word_exists_in_lut:
                    add_word_binary_to_segment(word)
                    conclude_segment_b64()

                    segment_header = "H2"
                    add_new_newline_segment(segment_header, char)
                    conclude_segment_ascii()

                    prev_segment_header = segment_header
                    word = ""

                elif segment_header == "H3" and not word_exists_in_lut:
                    conclude_segment_b64()

                    segment_header = "H2"
                    add_new_newline_segment(segment_header, char)
                    conclude_segment_ascii()

                    segment_header = "H1"
                    add_new_empty_segment(segment_header)
                    add_word_ascii_to_segment(word)
                    conclude_segment_ascii()

                    segment_header = "H2"
                    add_new_newline_segment(segment_header, char)
                    conclude_segment_ascii()

                    prev_segment_header = segment_header
                    word = ""

                elif segment_header == "H1" and word_exists_in_lut:
                    conclude_segment_ascii()

                    segment_header = "H2"
                    add_new_newline_segment(segment_header, char)
                    conclude_segment_ascii()

                    segment_header = "H3"
                    add_new_empty_segment(segment_header)
                    add_word_binary_to_segment(word)
                    conclude_segment_b64()

                    segment_header = "H2"
                    add_new_newline_segment(segment_header, char)
                    conclude_segment_ascii()

                    prev_segment_header = segment_header
                    word = ""

                elif segment_header == "H1" and not word_exists_in_lut:
                    add_word_ascii_to_segment(word)
                    conclude_segment_ascii()

                    segment_header = "H2"
                    add_new_newline_segment(segment_header, char)
                    conclude_segment_ascii()

                    prev_segment_header = segment_header
                    word = ""


    with open(ir_filename, 'w') as file:
        json.dump(ir, file)

if __name__ == '__main__':
    encode()
