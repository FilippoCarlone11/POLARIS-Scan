# POLARIS-Scan: scan-chain for b05 (NanGate 45nm)
# usage: polaris b05_45nm.tcl
set_operation chain
set_liberty /app/Tech/Syn_libraries/45nm/lib/NangateOpenCellLibrary_typical.lib
read_verilog 45nm/synthesis/b05.synth.v
set_output_name 45nm/scan/b05.chain.v
set_work_dir 45nm/scan
set_clock clk
