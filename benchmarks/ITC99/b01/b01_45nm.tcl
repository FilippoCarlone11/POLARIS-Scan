# Polaris: full flow for b01 (NanGate 45nm)
# usage: polaris b01_45nm.tcl
set_operation flow
set_tech 45nm
read_yosys b01_45nm.ys
set_clock clk
set_reset rst
