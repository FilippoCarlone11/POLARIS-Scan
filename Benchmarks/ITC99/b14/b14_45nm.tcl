# POLARIS-Scan: scan-chain for b14 (NanGate 45nm)
# usage: polaris b14_45nm.tcl
set_operation chain
set_liberty /app/Tech/Syn_libraries/45nm/lib/NangateOpenCellLibrary_typical.lib
read_verilog b14_45nm.synth.v
set_output_name b14_45nm.scan.v
set_work_dir log
set_clock clk
