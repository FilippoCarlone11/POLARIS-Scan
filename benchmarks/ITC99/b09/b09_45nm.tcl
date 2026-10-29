# Polaris: full flow for b09 (NanGate 45nm)
# usage: polaris b09_45nm.tcl
set_operation flow
set_tech 45nm
read_yosys b09_45nm.ys
set_clock clk
set_reset rst
