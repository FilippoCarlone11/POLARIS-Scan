# POLARIS-Scan: scan-chain for b02 (NanGate 45nm)
# usage: polaris b02_45nm.tcl
set_operation chain
set_liberty /app/Tech/Syn_libraries/45nm/lib/NangateOpenCellLibrary_typical.lib
read_verilog b02_45nm.synth.v
set_output_name b02_45nm.scan.v
set_work_dir log
set_clock clk
