# POLARIS-Scan: scan-chain for b07 (IHP SG13G2 130nm)
# usage: polaris b07_130nm.tcl
set_operation chain
set_liberty /app/Tech/Syn_libraries/130nm/lib/sg13g2_stdcell_typ_1p20V_25C.lib
read_verilog b07_130nm.synth.v
set_output_name b07_130nm.scan.v
set_work_dir log
set_clock clk
