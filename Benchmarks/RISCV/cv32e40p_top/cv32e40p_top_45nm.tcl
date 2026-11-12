# POLARIS-Scan: scan-chain for cv32e40p_top (NanGate 45nm)
# usage: polaris cv32e40p_top_45nm.tcl
set_operation chain
set_liberty /app/Tech/Syn_libraries/45nm/lib/NangateOpenCellLibrary_typical.lib
read_verilog cv32e40p_top_45nm.synth.v
set_output_name cv32e40p_top_45nm.scan.v
set_work_dir log
set_clock clk_i
