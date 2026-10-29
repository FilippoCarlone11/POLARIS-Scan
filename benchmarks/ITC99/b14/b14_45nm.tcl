# Polaris: full flow for b14 (NanGate 45nm)
# usage: polaris b14_45nm.tcl
set_operation flow
set_tech 45nm
read_yosys b14_45nm.ys
set_clock clk
set_reset rst
