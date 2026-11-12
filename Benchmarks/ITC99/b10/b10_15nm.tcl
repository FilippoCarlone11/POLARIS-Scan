# POLARIS-Scan: scan-chain for b10 (NanGate 15nm)
# usage: polaris b10_15nm.tcl
set_operation chain
set_liberty /app/Tech/Syn_libraries/15nm/CCS/NanGate_15nm_OCL_typical_conditional_ccs.lib
read_verilog 15nm/synthesis/b10.synth.v
set_output_name 15nm/scan/b10.chain.v
set_work_dir 15nm/scan
set_clock clk
