# Polaris: full flow for b04 (NanGate 45nm)
# usage: polaris b04_45nm.tcl
set_operation flow
set_tech 45nm
read_yosys b04_45nm.ys
set_clock clk
set_reset rst
