# Polaris: full flow for b19 (NanGate 45nm)
# usage: polaris b19_45nm.tcl
set_operation flow
set_tech 45nm
read_yosys b19_45nm.ys
set_clock clk
set_reset rst
