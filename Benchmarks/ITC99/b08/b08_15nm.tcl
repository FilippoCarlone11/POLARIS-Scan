# POLARIS-Scan: scan-chain for b08 (NanGate 15nm)
# usage: polaris b08_15nm.tcl
set_operation chain
set_liberty /app/Tech/Syn_libraries/15nm/CCS/NanGate_15nm_OCL_typical_conditional_ccs.lib
read_verilog 15nm/synthesis/b08.synth.v
set_output_name 15nm/scan/b08.chain.v
set_work_dir 15nm/scan
set_clock clk
