# Polaris: full flow for b03 (NanGate 45nm)
# usage: polaris b03_45nm.tcl
set_operation flow
set_tech 45nm
read_yosys b03_45nm.ys
set_clock clk
set_reset rst
