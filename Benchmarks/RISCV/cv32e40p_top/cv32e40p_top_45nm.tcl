# POLARIS-Scan: scan-chain for cv32e40p_top (NanGate 45nm)
# usage: polaris cv32e40p_top_45nm.tcl
set_operation chain
set_liberty /app/Tech/Syn_libraries/45nm/lib/NangateOpenCellLibrary_typical.lib
read_verilog 45nm/synthesis/cv32e40p_top.synth.v
set_output_name 45nm/scan/cv32e40p_top.chain.v
set_work_dir 45nm/scan
set_clock clk_i
