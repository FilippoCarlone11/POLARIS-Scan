# Polaris: full flow for b06 (NanGate 45nm)
# usage: polaris b06_45nm.tcl
set_operation flow
set_tech 45nm
read_yosys b06_45nm.ys
set_clock clk
set_reset rst
