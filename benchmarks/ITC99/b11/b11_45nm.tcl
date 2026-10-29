# Polaris: full flow for b11 (NanGate 45nm)
# usage: polaris b11_45nm.tcl
set_operation flow
set_tech 45nm
read_yosys b11_45nm.ys
set_clock clk
set_reset rst
