# POLARIS-Scan: scan-chain for b21 (NanGate 45nm)
# usage: polaris b21_45nm.tcl
set_operation chain
set_liberty /app/Tech/Syn_libraries/45nm/lib/NangateOpenCellLibrary_typical.lib
read_verilog b21_45nm.synth.v
set_output_name b21_45nm.scan.v
set_work_dir log
set_clock clk
