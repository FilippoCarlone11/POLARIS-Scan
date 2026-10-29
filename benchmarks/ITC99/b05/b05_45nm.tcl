# Polaris: full flow for b05 (NanGate 45nm)
# usage: polaris b05_45nm.tcl
set_operation flow
set_tech 45nm
read_yosys b05_45nm.ys
set_clock clk
set_reset rst
