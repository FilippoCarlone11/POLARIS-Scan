# Polaris: full flow for b02 (NanGate 45nm)
# usage: polaris b02_45nm.tcl
set_operation flow
set_tech 45nm
read_yosys b02_45nm.ys
set_clock clk
set_reset rst
