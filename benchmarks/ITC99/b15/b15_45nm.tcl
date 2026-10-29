# Polaris: full flow for b15 (NanGate 45nm)
# usage: polaris b15_45nm.tcl
set_operation flow
set_tech 45nm
read_yosys b15_45nm.ys
set_clock clk
set_reset rst
