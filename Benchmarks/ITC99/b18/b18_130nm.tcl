# POLARIS-Scan: scan-chain for b18 (IHP SG13G2 130nm)
# usage: polaris b18_130nm.tcl
set_operation chain
set_liberty /app/Tech/Syn_libraries/130nm/lib/sg13g2_stdcell_typ_1p20V_25C.lib
read_verilog 130nm/synthesis/b18.synth.v
set_output_name 130nm/scan/b18.chain.v
set_work_dir 130nm/scan
set_clock clk
