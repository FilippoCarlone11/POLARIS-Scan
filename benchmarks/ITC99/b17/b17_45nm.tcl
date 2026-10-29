# Polaris: full flow for b17 (NanGate 45nm)
# usage: polaris b17_45nm.tcl
set_operation flow
set_tech 45nm
read_yosys b17_45nm.ys
set_clock clk
set_reset rst
