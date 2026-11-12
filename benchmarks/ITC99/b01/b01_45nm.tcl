# Polaris: scan-chain for b01 (NanGate 45nm)
# usage: polaris b01_45nm.tcl
set_operation chain
set_liberty /Tech/Syn_libraries/45nm/lib/NangateOpenCellLibrary_typical.lib 
read_verilog b01_45nm.synth.v
set_clock clk
set_reset rst
