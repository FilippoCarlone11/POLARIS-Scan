# POLARIS-Scan: scan-chain for b22 (NanGate 15nm)
# usage: polaris b22_15nm.tcl
set_operation chain
set_liberty /app/Tech/Syn_libraries/15nm/CCS/NanGate_15nm_OCL_typical_conditional_ccs.lib
read_verilog b22_15nm.synth.v
set_output_name b22_15nm.scan.v
set_work_dir log
set_clock clk
