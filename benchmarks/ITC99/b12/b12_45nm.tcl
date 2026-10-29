# Polaris: full flow for b12 (NanGate 45nm)
# usage: polaris b12_45nm.tcl
set_operation flow
set_tech 45nm
read_yosys b12_45nm.ys
set_clock clk
set_reset rst
