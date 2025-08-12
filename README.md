# Proof-of-Concept: Context-Aware Composable Compression Protocol (CCCP)

This Proof-of-Concept (POC) demonstrates how the [CCCP](https://github.com/brucekaushik/cccp) enables interaction between the SDK and vendor-specific encoders/decoders.

It showcases a staged vendor-based compression approach via a base SDK and vendor-specific encoders/decoders, where the second stage slightly inflates the output compared to the first intentionally. The **Vendors Package** represents the vendor-specific SDK implementation. In a full implementation, this would ideally be global (one per device) and installable via:

```bash
cccp install VendorName:PackageName@Version
```

For example:

```bash
cccp install Knolbay:Poc1@1.0.0
```

This would fetch:

- The associated LUT (agnostic of programming language)
- The relevant encoders & decoders (programming language–specific)

A future enhancement could include a flag to retrieve encoders/decoders in a specific programming language.

## Programming Language & Terminology used in the POC

- Python 3.8 and above is required for running the POC.
- For terminology please refer to the main [CCCP spec](https://github.com/brucekaushik/cccp).

## Quick Start

Clone the repo and run the POC end-to-end with:

```bash
python3 app.py
```

### Input

```
input_output/input2.txt
```

### Outputs

```
input_output/input2_ir1.json       # stage 1: IR generated from input
input_output/input2_bin1.cccp      # stage 1: binary generated from IR
input_output/input2_ir1_rec.json   # stage 1: reconstructed IR from binary
input_output/input2_rec1.txt       # stage 1: reconstructed text from IR

input_output/input2_ir2.json       # stage 2: IR generated from stage 1 IR
input_output/input2_bin2.cccp      # stage 2: binary generated from IR
input_output/input2_ir2_rec.json   # stage 2: reconstructed IR from binary
input_output/input2_rec2.txt       # stage 2: reconstructed text from IR
```

## Current Limitations

This POC **does not** focus on:

- Encoding/decoding performance (RAM & CPU usage) or throughput (Mbps)
- Complete streamability (planned via [SFOR](https://github.com/brucekaushik/sfor) in the future)
- Production-level code quality (e.g., error handling)

## Demonstrated Features

- Vendorization via a base SDK and vendor-specific encoders/decoders
- Full CCCP pipeline: **Text → IR (multi-stage) → Binary**
- Generic compression gains
- Handling of unencoded data through exclusion mechanisms

## Current Architecture

ASCII text, encoders and decoders are used by the SDK to keep it simple.

### App

```
app.py
```

This script demonstrates the complete CCCP encoding–decoding pipeline in two stages:

- **Stage 1:**

  - Converts a text file → JSON IR → binary CCCP → back to JSON IR → back to original text.
  - Verifies integrity at each step using MD5 hashes.

- **Stage 2:**

  - Reuses the same IR object, adds a new header, and repeats the binary round-trip.
  - Shows that IR can be updated and re-encoded without re-parsing the original text.
  - Ensures that both the intermediate IR and final text are bit-for-bit identical to their sources after each round trip. *(In this POC, stage 2 output is slightly larger due to different headers and compression context.)*

The SDK's packer/unpacker classes (`AsciiToJsonIr`, `JsonIrToBin`, `BinToJsonIr`, `JsonIrToAscii`) call predefined methods, thereby enforcing the expected behavior of vendor-specific implementations via duck typing at runtime. While formal base contracts for these methods are defined in cccp.codec.contracts (and can be implemented by vendors), the SDK does not require inheritance — the object type is treated as an interface rather than a strict base class.

### Encoders (SDK Layer)

```
cccp.codec.packers.AsciiToJsonIr
cccp.codec.packers.JsonIrToBin
```

SDK's packer classes mentioned above.

### Decoders (SDK Layer)

```
cccp.codec.unpackers.BinToJsonIr
cccp.codec.unpackers.JsonIrToAscii
```

SDK's unpacker classes mentioned above.

### Interfaces

```
cccp.codec.context.IrContext
```

Current interface used by the SDK's packer and unpacker classes (`AsciiToJsonIr`, `JsonIrToBin`, `BinToJsonIr`, `JsonIrToAscii`). It defines a common contract for working with **Intermediate Representation (IR)** objects within the SDK layer.

Vendor-specific implementations do **not** use this interface — they follow a separate, duck-typed runtime contract (see *Contracts* below). In future, `IrContext` may be split into dedicated packer and unpacker interfaces; its current form is intentionally minimal and provisional.

### Contracts

```
cccp.codec.contracts.BaseAsciiToJsonIr
cccp.codec.contracts.BaseJsonIrToBin
cccp.codec.contracts.BaseBinToJsonIr
cccp.codec.contracts.BaseJsonIrToAscii
```

Base contracts implemented by vendor-specific packers and unpackers.

Unlike `IrContext`, these are **not statically type-checked** — the SDK validates them at runtime using duck typing.

They define the expected methods and behaviors for each transformation stage so that different vendor implementations can be plugged into the CCCP pipeline without modifying SDK code.

### Types

```
cccp.codec.types.JsonIrSegment
cccp.codec.types.JsonIr
cccp.codec.types.VendorLutDict
cccp.codec.types.VendorLutMetaDict
cccp.codec.types.PartiallyProcessedPayloadTuple
cccp.codec.types.PayloadBitlenAndPayload
cccp.codec.types.PayloadBytesAndSymbolCount
```

A set of shared type definitions used across both SDK and vendor layers.

They provide a common vocabulary for IR structures, lookup tables, and intermediate payload formats, helping keep data consistent as it moves between stages of the CCCP pipeline.

### Utils

```
cccp.codec.bitmath
cccp.codec.transformers
cccp.codec.vendor
```

Supporting utility modules for bit-level operations, data transformations, and vendor resolution/management.

### Vendor1: LUT, LUT Meta Data, Encoder, Decoder (Implementation Layer)

The implementation uses a Lookup Table containing 3,70,099 unique words, each represented with a 19-bit symbol width which keeps it somewhat real.

Let’s assume Vendor1 is represented uniquely by the sign `Knolbay:Poc1@1.0.0`

```
cccp.codec.Knolbay.Poc1.v1_0_0/lut_map.json
cccp.codec.Knolbay.Poc1.v1_0_0/lut_meta.json
cccp.codec.Knolbay.Poc1.v1_0_0.packers.AsciiToJsonIr
cccp.codec.Knolbay.Poc1.v1_0_0.packers.JsonIrToBin
cccp.codec.Knolbay.Poc1.v1_0_0.unpackers.BinToJsonIr
cccp.codec.Knolbay.Poc1.v1_0_0.unpackers.JsonIrToAscii
```

> For such simple transformations, the SDK alone would usually be sufficient, without requiring vendor-specific encoders/decoders. However, in this POC, vendorization is demonstrated explicitly — so the LUT logic is shown in separate vendor classes. In a real-world implementation, this could be replaced with a simple SDK-only flow, optionally keeping a vendor “hook” for extension.

### Vendor2: LUT, LUT Meta Data, Encoder, Decoder (Implementation Layer)

The implementation uses a Lookup Table containing 3,70,099 unique words, each represented with a 19-bit symbol width which keeps it somewhat real.

Let’s assume Vendor2 is represented uniquely by the sign `Knolbay:Poc2@1.0.0`

```
cccp.codec.Knolbay.Poc2.v1_0_0/lut_map.json
cccp.codec.Knolbay.Poc2.v1_0_0/lut_meta.json
cccp.codec.Knolbay.Poc2.v1_0_0.packers.AsciiToJsonIr
cccp.codec.Knolbay.Poc2.v1_0_0.packers.JsonIrToBin
cccp.codec.Knolbay.Poc2.v1_0_0.unpackers.BinToJsonIr
cccp.codec.Knolbay.Poc2.v1_0_0.unpackers.JsonIrToAscii
```

> For such simple transformations, the SDK alone would usually be sufficient, without requiring vendor-specific encoders/decoders. However, in this POC, vendorization is demonstrated explicitly — so the LUT logic is shown in separate vendor classes. In a real-world implementation, this could be replaced with a simple SDK-only flow, optionally keeping a vendor “hook” for extension.

## 📜 License

This POC is under active development. Licensed under [MIT](LICENSE).

## ✍️ Author

Made by [Nanduri Srinivas Koushik](https://www.linkedin.com/in/brucekaushik/).

Ideas, suggestions, constructive criticism, and contributions are always welcome. Whether it’s proposing improvements, pointing out flaws, or sharing new use cases — your input helps make SFOR better.
