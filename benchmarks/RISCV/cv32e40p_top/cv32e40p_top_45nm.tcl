# Polaris: chain -> cut -> bench for cv32e40p_top (NanGate 45nm)
# the netlist is already synthesized, so the synthesis is skipped
# usage: polaris cv32e40p_top_45nm.tcl
set_operation chain cut bench
set_tech 45nm
read_verilog cv32e40p_top.v
set_clock clk_i
set_reset rst_ni
