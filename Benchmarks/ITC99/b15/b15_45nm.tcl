# POLARIS-Scan: scan-chain for b15 (NanGate 45nm)
# usage: polaris b15_45nm.tcl
set_operation chain
set_liberty /app/Tech/Syn_libraries/45nm/lib/NangateOpenCellLibrary_typical.lib
read_verilog b15_45nm.synth.v
set_output_name b15_45nm.scan.v
set_work_dir log
set_clock clk
