# Polaris-Scan v.0.1

This guide provides the basic instructions to build, configure, and run the tool.

## Build and Run

To compile and prepare the environment, use the provided Makefile. Run the following commands in your terminal:

```bash
make build
make run
```

## Configuration

Before executing Polaris-Scan, you need to create a TCL configuration file to define the parameters for your run. 

Inside the Benchmark directory you can find some examples of TCL files.

This is the configuration for ITC'99 B01 (`b01_15nm.tcl`):

```tcl
set_operation chain
set_liberty /app/Tech/Syn_libraries/15nm/CCS/NanGate_15nm_OCL_typical_conditional_ccs.lib
read_verilog 15nm/synthesis/b0 synth.v
set_output_name 15nm/scan/b0 chain.v
set_work_dir 15nm/scan
set_clock clk
```

## Execution

Once your tool is built and your `.tcl` script is ready, you can execute Polaris-Scan by passing the configuration file to the main command:

```bash
polaris b01_15nm.tcl
```

## License & Third-Party Assets

The source code of this project is licensed under the **MIT License** (see the `LICENSE` file for details).

### Nangate 15nm and 45nm Open Cell Library
The standard cell library files located in `Tech/45nm/lib` and in `Tech/15nm/CCS` (used solely to demonstrate and verify this project) are **not** covered by the MIT License. They were developed by Nangate Inc. and are subject to the **Nangate Open Cell Library License, Version 1.0** (see `Tech/45nm/lib/LICENSE`). 

Per the Nangate license terms, these specific files are provided for **non-commercial, academic, and research purposes only**. Commercial use or fabrication using these library files is strictly prohibited without prior permission from Nangate/Silvaco.

### IHP Open Source PDK
Verification and benchmarking were performed using the **IHP Open Source PDK (130nm SG13G2)**, developed by IHP GmbH. 

* **License:** The IHP Open PDK files (located in `Tech/130nm/lib` or linked as a submodule) are licensed under the **Apache License 2.0**, permitting both academic and commercial use.
*