# Polaris: full flow for b20 (NanGate 45nm)
# usage: polaris b20_45nm.tcl
set_operation flow
set_tech 45nm
read_yosys b20_45nm.ys
set_clock clk
set_reset rst
