# POLARIS-Scan: scan-chain for b01 (NanGate 45nm)
# usage: polaris b01_45nm.tcl
set_operation chain
set_liberty /app/Tech/Syn_libraries/45nm/lib/NangateOpenCellLibrary_typical.lib
read_verilog b0_synth.v
set_output_name b0_chain.v
set_clock clk
