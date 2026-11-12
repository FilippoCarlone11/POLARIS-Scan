# POLARIS-Scan: scan-chain for b03 (NanGate 45nm)
# usage: polaris b03_45nm.tcl
set_operation chain
set_liberty /app/Tech/Syn_libraries/45nm/lib/NangateOpenCellLibrary_typical.lib
read_verilog b03_45nm.synth.v
set_output_name b03_45nm.scan.v
set_work_dir log
set_clock clk
