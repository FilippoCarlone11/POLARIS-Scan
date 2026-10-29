# Polaris: full flow for b07 (NanGate 45nm)
# usage: polaris b07_45nm.tcl
set_operation flow
set_tech 45nm
read_yosys b07_45nm.ys
set_clock clk
set_reset rst
