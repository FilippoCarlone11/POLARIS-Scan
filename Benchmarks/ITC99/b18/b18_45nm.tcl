# POLARIS-Scan: scan-chain for b18 (NanGate 45nm)
# usage: polaris b18_45nm.tcl
set_operation chain
set_liberty /app/Tech/Syn_libraries/45nm/lib/NangateOpenCellLibrary_typical.lib
read_verilog 45nm/synthesis/b18.synth.v
set_output_name 45nm/scan/b18.chain.v
set_work_dir 45nm/scan
set_clock clk
