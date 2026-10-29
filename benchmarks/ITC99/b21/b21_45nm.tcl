# Polaris: full flow for b21 (NanGate 45nm)
# usage: polaris b21_45nm.tcl
set_operation flow
set_tech 45nm
read_yosys b21_45nm.ys
set_clock clk
set_reset rst
