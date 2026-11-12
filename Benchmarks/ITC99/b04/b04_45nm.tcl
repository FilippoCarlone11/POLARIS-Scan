# POLARIS-Scan: scan-chain for b04 (NanGate 45nm)
# usage: polaris b04_45nm.tcl
set_operation chain
set_liberty /app/Tech/Syn_libraries/45nm/lib/NangateOpenCellLibrary_typical.lib
read_verilog 45nm/synthesis/b04.synth.v
set_output_name 45nm/scan/b04.chain.v
set_work_dir 45nm/scan
set_clock clk
