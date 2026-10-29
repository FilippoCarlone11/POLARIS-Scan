# Polaris: full flow for b22 (NanGate 45nm)
# usage: polaris b22_45nm.tcl
set_operation flow
set_tech 45nm
read_yosys b22_45nm.ys
set_clock clk
set_reset rst
