# Polaris: full flow for b13 (NanGate 45nm)
# usage: polaris b13_45nm.tcl
set_operation flow
set_tech 45nm
read_yosys b13_45nm.ys
set_clock clk
set_reset rst
