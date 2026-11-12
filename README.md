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