# read_vcd_activities gcd
define_corners ss ff
read_liberty -corner ss simple_Late.lib
read_liberty -corner ff simple_Early.lib
read_verilog simple.v
link_design simple

read_sdc simple.sdc
#read_spef gcd_sky130hd.spef

# 2 corners with +/- 10% derating example
set_timing_derate -early 0.9
set_timing_derate -late  1.1

#create_clock -name clk -period 10 {clk1 clk2 clk3}
#set_input_delay -clock clk 0 {in1 in2}
#
# report all corners
report_checks -path_delay min_max
# report typical corner
report_checks -corner ss

report_checks -corner ff
