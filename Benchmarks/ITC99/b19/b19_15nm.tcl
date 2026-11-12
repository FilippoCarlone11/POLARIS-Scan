# POLARIS-Scan: scan-chain for b19 (NanGate 15nm)
# usage: polaris b19_15nm.tcl
set_operation chain
set_liberty /app/Tech/Syn_libraries/15nm/CCS/NanGate_15nm_OCL_typical_conditional_ccs.lib
read_verilog b19_15nm.synth.v
set_output_name b19_15nm.scan.v
set_work_dir log
set_clock clk
